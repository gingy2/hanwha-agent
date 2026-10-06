from __future__ import annotations

from pathlib import Path                                          # 파일 경로를 객체로 다루기

from app.core.logging import get_logger                           # 로거 생성 함수
from app.integrations.ports import ParsedBlock, ParsedDoc         # 파서 결과 형식 (블록 하나 / 문서 전체)

log = get_logger(__name__)                                        # 이 모듈 전용 로거


# ─────────────────────────── 설정 ───────────────────────────

# PDF 적재 시 표를 따로 떼어 읽을지: 환경변수 → .env 순서로 PDF_TABLES 값 확인
def pdf_tables_on() -> bool:
    import os                                                     # 환경변수 읽기

    raw = os.environ.get("PDF_TABLES")                            # 1순위: 실행 환경의 환경변수
    if raw is None:                                               # 없으면
        from dotenv import dotenv_values                          # .env 파일 읽기 도구

        raw = dotenv_values(".env").get("PDF_TABLES")             # 2순위: .env 파일 값
    return str(raw or "").strip().lower() in ("1", "true", "yes", "on")   # 켜짐으로 볼 값들


# ─────────────────────────── 공용 도우미 ───────────────────────────

# 표의 머리글과 나머지 행들을 마크다운 표 한 덩어리로 변경하는 함수
def _table_to_markdown(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"                       # | 부서 | 1분기 | ...
    sep = "|" + "---|" * len(headers)                              # |---|---|... (머리글 구분선)
    body = ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]   # 데이터 행들
    return "\n".join([head, sep, *body])                           # 줄바꿈으로 이어 붙여 한 덩어리


# 셀 값 하나를 표에 넣기 좋은 한 줄 문자열로 정리
def _cell(value) -> str:
    if value is None:                                              # 빈 칸이면
        return ""                                                  # 빈 문자열
    return " ".join(str(value).split())                            # 줄바꿈·연속 공백을 공백 하나로 (마크다운 표가 안 깨지게)


# ─────────────────────────── PDF ───────────────────────────

# PDF 파서 함수 (기본) : pypdf로 페이지 단위로 읽어 ParsedDoc으로 리턴. 표는 구분하지 않음
def parse_pdf(path: Path) -> ParsedDoc:
    from pypdf import PdfReader                                   # PDF 읽기 라이브러리 (쓸 때만 import)

    reader = PdfReader(str(path))                                 # PDF 열기
    blocks: list[ParsedBlock] = []                                # 결과 블록 목록

    for page_no, page in enumerate(reader.pages, 1):              # 1쪽부터 한 쪽씩
        text = (page.extract_text() or "").strip()                # 쪽의 글자 추출 (없으면 빈 문자열)
        if not text:                                              # 글자가 하나도 없으면
            log.info("텍스트 없음 (스캔본으로 보임): %s p.%d", path.name, page_no)   # 스캔본 의심 기록
            continue                                              # 이 쪽은 건너뜀
        blocks.append(ParsedBlock("조항", f"p.{page_no}", text))   # 쪽 하나 = 블록 하나

    return ParsedDoc(blocks=blocks, page_count=len(reader.pages), table_count=0)   # 표는 따로 못 잡음 → 0


# PDF 파서 함수 (표 분리) : pdfplumber로 표는 표 블록, 표 밖 글자는 조항 블록으로 (PDF_TABLES=on 일 때)
def parse_pdf_tables(path: Path) -> ParsedDoc:
    import pdfplumber                                             # 표 인식이 되는 PDF 라이브러리

    blocks: list[ParsedBlock] = []                                # 결과 블록 목록
    n_tables = 0                                                  # 찾은 표 수
    with pdfplumber.open(str(path)) as pdf:                       # PDF 열기
        page_count = len(pdf.pages)                               # 전체 쪽 수
        for page_no, page in enumerate(pdf.pages, 1):             # 한 쪽씩
            found = page.find_tables()                            # 이 쪽의 표들
            boxes = [t.bbox for t in found]       # (x0, top, x1, bottom)   # 표마다 사각형 영역

            # 글자 하나가 어느 표 상자에도 들어있지 않으면 True (표 글자가 본문에 중복되지 않게)
            def outside(obj, boxes=boxes) -> bool:                # boxes=boxes: 이 쪽의 표 영역을 함수에 고정
                x0, top = obj.get("x0", 0), obj.get("top", 0)     # 글자의 왼쪽·위 좌표
                x1, bottom = obj.get("x1", 0), obj.get("bottom", 0)   # 글자의 오른쪽·아래 좌표
                return not any(b[0] <= x0 and x1 <= b[2] and b[1] <= top and bottom <= b[3]   # 어떤 표 상자 안에도
                               for b in boxes)                    # 완전히 들어 있지 않으면 표 밖

            text = ((page.filter(outside) if boxes else page).extract_text() or "").strip()   # 표 밖 글자만 추출
            if text:                                              # 본문 글자가 있으면
                blocks.append(ParsedBlock("조항", f"p.{page_no}", text))   # 조항 블록
            for k, table in enumerate(found, 1):                  # 표마다
                rows = [[_cell(c) for c in row] for row in table.extract()]   # 셀 글자 2차원 리스트
                if not any(any(row) for row in rows):             # 모든 셀이 비었으면
                    continue                                      # 건너뜀 (선만 있는 가짜 표)
                blocks.append(ParsedBlock("표", f"p.{page_no} · 표{k}",
                                          _table_to_markdown(rows[0], rows[1:])))   # 마크다운 표 블록
                n_tables += 1                                     # 표 수 증가
            if not text and not found:                            # 글자도 표도 없으면
                log.info("텍스트 없음 (스캔본으로 보임): %s p.%d", path.name, page_no)   # 스캔본 의심 기록

    return ParsedDoc(blocks=blocks, page_count=page_count, table_count=n_tables)


# ─────────────────────────── DOCX / HWPX ───────────────────────────

# DOCX를 본문 순서 그대로 읽어 ParsedDoc 으로 리턴하는 함수
def parse_docx(path: Path) -> ParsedDoc:
    from docx import Document                                     # Word 문서 열기
    from docx.table import Table                                  # XML 요소 → 표 객체
    from docx.text.paragraph import Paragraph                     # XML 요소 → 문단 객체

    doc = Document(str(path))                                     # 파일 열기
    blocks: list[ParsedBlock] = []                                # 결과 블록 목록
    tables = 0                                                    # 표 번호 세기

    body = doc.element.body                                       # 본문 XML
    for child in body.iterchildren():                             # 본문 요소를 순서대로 (문단·표가 섞인 원래 순서)
        tag = child.tag.split("}")[-1]                            # 네임스페이스 떼고 태그 이름만 (p 또는 tbl)
        if tag == "p":                                            # 문단이면
            text = Paragraph(child, doc).text.strip()             # 문단 글자
            if text:                                              # 빈 문단이 아니면
                blocks.append(ParsedBlock("조항", f"{path.stem}", text))   # 위치는 파일 이름
        elif tag == "tbl":                                        # 표면
            table = Table(child, doc)                             # 표 객체로
            rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]   # 행 × 셀 글자 2차원 리스트
            if not rows:                                          # 빈 표면
                continue                                          # 건너뜀
            tables += 1                                           # 표 번호 증가
            blocks.append(
                ParsedBlock("표", f"표{tables}", _table_to_markdown(rows[0], rows[1:]))   # 첫 행 = 머리글, 나머지 = 데이터
            )

    return ParsedDoc(blocks=blocks, page_count=1, table_count=tables)   # docx는 쪽 개념이 없어 1


# HWPX 파싱해서 ParsedDoc 으로 리턴하는 함수
def parse_hwpx(path: Path) -> ParsedDoc:
    import re                                                      # 섹션 파일 이름 찾기용
    import zipfile                                                 # hwpx = XML 묶음 zip
    from xml.etree import ElementTree as ET                        # XML 읽기

    ns_p = "{http://www.hancom.co.kr/hwpml/2011/paragraph}"        # 한글 문단 XML 네임스페이스
    blocks: list[ParsedBlock] = []                                 # 결과 블록 목록
    tables = 0                                                     # 표 번호 세기

    with zipfile.ZipFile(path) as zf:                              # zip으로 열기
        sections = sorted(n for n in zf.namelist()
                          if re.match(r"Contents/section\d+\.xml$", n))   # 본문 섹션 파일들 (순서대로)
        for name in sections:                                      # 섹션마다
            root = ET.fromstring(zf.read(name))                    # XML 파싱

            for para in root.findall(f"{ns_p}p"):                  # 최상위 문단마다
                table_el = para.find(f".//{ns_p}tbl")              # 문단 안에 표가 있는지
                if table_el is not None:                           # 표가 있으면
                    tables += 1                                    # 표 번호 증가
                    rows: list[list[str]] = []                     # 표 내용
                    for tr in table_el.findall(f"{ns_p}tr"):       # 행마다
                        cells = []                                 # 이 행의 셀 글자
                        for tc in tr.findall(f"{ns_p}tc"):         # 셀마다
                            cells.append("".join(
                                t.text or "" for t in tc.iter(f"{ns_p}t")   # 셀 안 글자 조각(t)을 이어 붙임
                            ).strip())
                        rows.append(cells)                         # 행 추가
                    if rows:                                       # 내용이 있으면
                        blocks.append(ParsedBlock(
                            "표", f"표{tables}", _table_to_markdown(rows[0], rows[1:])   # 마크다운 표 블록
                        ))
                    continue                                       # 표 문단은 글자 처리 안 함 (중복 방지)
                text = "".join(t.text or "" for t in para.iter(f"{ns_p}t")).strip()   # 문단 안 글자 조각을 이어 붙임
                if text:                                           # 빈 문단이 아니면
                    blocks.append(ParsedBlock("조항", path.stem, text))   # 위치는 파일 이름

    return ParsedDoc(blocks=blocks, page_count=1, table_count=tables)   # 쪽 정보 없음 → 1


# ─────────────────────────── XLSX ───────────────────────────

# 병합 셀 채우기: 병합 범위의 모든 칸에 왼쪽 위 칸 값을 복사 (None으로 비는 문제 해결)
def _fill_merged(ws) -> list[list]:
    grid = [list(row) for row in ws.iter_rows(values_only=True)]   # 시트 값을 2차원 리스트로
    if not grid:                                                   # 빈 시트면
        return grid                                                # 그대로
    r0, c0 = ws.min_row, ws.min_column                             # 데이터가 시작하는 행·열 (grid[0][0]의 실제 위치)
    for rng in ws.merged_cells.ranges:                             # 병합 범위마다
        top_left = grid[rng.min_row - r0][rng.min_col - c0]        # 실제 값이 들어 있는 왼쪽 위 칸
        for r in range(rng.min_row, rng.max_row + 1):              # 범위의 모든 행
            for c in range(rng.min_col, rng.max_col + 1):          # 범위의 모든 열
                grid[r - r0][c - c0] = top_left                    # 같은 값으로 채움
    return grid


# 계산값이 없는 수식 칸 표시: data_only로 None이 된 칸에 수식 원문을 넣어 둠
def _fill_formulas(grid: list[list], ws, ws_formula) -> list[list]:
    r0, c0 = ws.min_row, ws.min_column                             # grid[0][0]의 실제 위치
    for i, row in enumerate(grid):                                 # 행마다
        for j, value in enumerate(row):                            # 칸마다
            if value is not None:                                  # 값이 있으면
                continue                                           # 그대로
            formula = ws_formula.cell(row=r0 + i, column=c0 + j).value   # 수식 모드로 연 시트의 같은 칸
            if isinstance(formula, str) and formula.startswith("="):     # 수식이면
                row[j] = f"{formula} (계산값 없음)"                   # 저장된 계산값이 없다는 표시와 함께 넣음
    return grid


# 한 시트에 표가 여러 개면 빈 행을 경계로 나누기 → [(시작 행 번호, 행들), ...]
def _split_regions(grid: list[list], first_row: int) -> list[tuple[int, list[list]]]:
    regions: list[tuple[int, list[list]]] = []                     # 결과
    for i, row in enumerate(grid):                                 # 행마다
        if all(c is None for c in row):                            # 완전히 빈 행은
            continue                                               # 경계로 보고 건너뜀
        if regions and regions[-1][0] + len(regions[-1][1]) == first_row + i:   # 바로 앞 행에 이어지면
            regions[-1][1].append(row)                             # 같은 표에 추가
        else:                                                      # 빈 행 뒤 첫 행이면
            regions.append((first_row + i, [row]))                 # 새 표 시작
    if len(regions) > 1:                                           # 표가 여러 개면
        for _, rows in regions:                                    # 표마다
            width = max(max((j + 1 for j, c in enumerate(r) if c is not None), default=0) for r in rows)   # 실제 값이 있는 마지막 열까지의 폭
            rows[:] = [r[:width] for r in rows]                    # 오른쪽 빈 열 잘라내기 (다른 표의 열 폭 제거)
    return regions


# 표 하나를 마크다운으로: 맨 위 병합 제목줄은 제목으로, 2단 머리글은 한 줄로 합침
def _xlsx_table(ws, top: int, rows: list[list[str]]) -> str:
    # 해당 행에 가로로 병합된 칸이 있는지
    def merged_across(row_no: int) -> bool:
        return any(r.min_row == row_no and r.max_col > r.min_col for r in ws.merged_cells.ranges)

    title = ""                                                     # 표 제목 (없으면 빈 문자열)
    if len(rows) > 2 and len(set(rows[0])) == 1 and len(rows[0]) > 1 and merged_across(top):   # 첫 행이 가로 병합된 같은 값 하나면
        title, rows, top = rows[0][0], rows[1:], top + 1           # 제목으로 떼어 내고 한 행 아래부터 표
    header, body = rows[0], rows[1:]                               # 머리글, 데이터
    if body and merged_across(top):                                # 머리글 행이 가로 병합이면 → 2단 머리글
        second = body[0]                                           # 아래 머리글 행
        header = [a if a == b or not b else (b if not a else f"{a} {b}") for a, b in zip(header, second)]   # 위·아래 머리글 합치기 (예: '상반기 1분기')
        body = body[1:]                                            # 아래 머리글 행은 데이터에서 제외
    table = _table_to_markdown(header, body)                       # 마크다운 표
    return f"{title}\n\n{table}" if title else table               # 제목이 있으면 표 위에 붙임


# XLSX 파싱해 ParsedDoc으로 리턴하는 함수
def parse_xlsx(path: Path) -> ParsedDoc:
    from openpyxl import load_workbook                             # 엑셀 읽기 라이브러리

    wb = load_workbook(str(path), data_only=True)                  # 값 모드 (수식 대신 저장된 계산값)
    wb_formula = load_workbook(str(path))                          # 수식 모드 (계산값이 없을 때 수식 원문 확인용)
    blocks: list[ParsedBlock] = []                                 # 결과 블록 목록

    for ws in wb.worksheets:                                       # 시트마다
        grid = _fill_formulas(_fill_merged(ws), ws, wb_formula[ws.title])   # 병합 칸 채우기 → 수식 칸 표시
        regions = _split_regions(grid, ws.min_row)                 # 빈 행 기준으로 표 나누기
        for k, (top, region) in enumerate(regions, 1):             # 표마다
            rows = [["" if c is None else str(c) for c in row] for row in region]   # 빈 칸은 '', 나머지는 문자열
            locator = ws.title if len(regions) == 1 else f"{ws.title} · 표{k}"      # 표가 하나면 시트 이름만
            blocks.append(ParsedBlock("표", locator, _xlsx_table(ws, top, rows)))   # 표 블록

    return ParsedDoc(
        blocks=blocks, page_count=len(wb.worksheets), table_count=len(blocks)   # 쪽 수 = 시트 수
    )


# ─────────────────────────── PPTX ───────────────────────────

# 그룹으로 묶인 도형 안쪽까지 펼쳐서 하나씩 돌려줌
def _walk_shapes(shapes):
    from pptx.shapes.group import GroupShape                       # 그룹 도형 타입

    for shape in shapes:                                           # 도형마다
        if isinstance(shape, GroupShape):                          # 그룹이면
            yield from _walk_shapes(shape.shapes)                  # 안쪽 도형들을 다시 펼침 (재귀)
        else:
            yield shape                                            # 일반 도형은 그대로


# PPT 표 도형 → 마크다운 표 (빈 표면 '')
def _pptx_table(shape) -> str:
    rows = [[_cell(cell.text) for cell in row.cells] for row in shape.table.rows]   # 셀 글자 2차원 리스트
    if not any(any(row) for row in rows):                          # 모든 셀이 비었으면
        return ""                                                  # 버림
    return _table_to_markdown(rows[0], rows[1:])                   # 첫 행 = 머리글


# PPT 차트 도형 → 데이터 표 (항목 × 계열)
def _pptx_chart(shape) -> str:
    chart = shape.chart                                            # 차트 객체
    try:
        categories = [_cell(c) for c in chart.plots[0].categories]   # 가로축 항목들
    except (IndexError, AttributeError, TypeError):                # 항목을 읽을 수 없는 차트면
        return ""                                                  # 버림
    series = list(chart.series)                                    # 계열(범례)들
    if not categories or not series:                               # 데이터가 없으면
        return ""                                                  # 버림

    # 3000.0 → '3000' 처럼 정수인 실수는 소수점 없이
    def num(v) -> str:
        return _cell(int(v) if isinstance(v, float) and v.is_integer() else v)

    header = ["항목", *(_cell(s.name) for s in series)]             # 머리글: 항목 | 계열1 | 계열2 ...
    body = [[cat, *(num(s.values[i]) if i < len(s.values) else "" for s in series)]   # 항목마다 계열 값
            for i, cat in enumerate(categories)]
    table = _table_to_markdown(header, body)                       # 마크다운 표
    title = chart.chart_title.text_frame.text.strip() if chart.has_title else ""   # 차트 제목
    return f"{title}\n\n{table}" if title else table               # 제목이 있으면 표 위에 붙임


# PPTX 파싱해 ParsedDoc으로 리턴하는 함수 (글자 + 표 + 차트)
def parse_pptx(path: Path) -> ParsedDoc:
    from pptx import Presentation                                  # PPT 읽기 라이브러리

    prs = Presentation(str(path))                                  # 파일 열기
    blocks: list[ParsedBlock] = []                                 # 결과 블록 목록
    n_tables = 0                                                   # 표 + 차트 수

    for page_no, slide in enumerate(prs.slides, 1):                # 1번 슬라이드부터
        lines = [shape.text.strip() for shape in _walk_shapes(slide.shapes)   # 그룹 안쪽까지 도형 중
                 if shape.has_text_frame and shape.text.strip()]   # 글자가 있는 것만 모음
        if slide.has_notes_slide:                                  # 발표자 노트가 있으면
            note = slide.notes_slide.notes_text_frame.text.strip()   # 노트 글자
            if note:                                               # 비어 있지 않으면
                lines.append(f"[발표자 노트] {note}")               # 표시를 붙여 추가
        if lines:                                                  # 내용이 있으면
            blocks.append(ParsedBlock("조항", f"슬라이드 {page_no}", "\n".join(lines)))   # 슬라이드 글자 = 블록 하나
        shapes = list(_walk_shapes(slide.shapes))                  # 슬라이드의 모든 도형 (펼친 것)
        tables = [md for md in (_pptx_table(s) for s in shapes if s.has_table) if md]   # 표 도형 → 마크다운 (빈 것 제외)
        charts = [md for md in (_pptx_chart(s) for s in shapes if s.has_chart) if md]   # 차트 도형 → 마크다운 (빈 것 제외)
        for k, md in enumerate(tables, 1):                         # 표마다
            blocks.append(ParsedBlock("표", f"슬라이드 {page_no} · 표{k}", md))     # 표 블록
        for k, md in enumerate(charts, 1):                         # 차트마다
            blocks.append(ParsedBlock("표", f"슬라이드 {page_no} · 차트{k}", md))   # 차트도 표 블록으로
        n_tables += len(tables) + len(charts)                      # 표 수 누적

    return ParsedDoc(blocks=blocks, page_count=len(prs.slides), table_count=n_tables)   # 쪽 수 = 슬라이드 수


# ─────────────────────────── 분기 ───────────────────────────

# 읽을 수 없는 형식별 변환 안내 문구
_CONVERT_HINT = {
    ".hwp": "한글에서 열고 [다른 이름으로 저장] → HWPX 또는 PDF 로 내보내세요. "
            "구 .hwp 는 한컴 독자 바이너리라 열지 않고는 읽을 방법이 없습니다",
    ".doc": "Word 에서 열고 .docx 로 저장하세요",
    ".ppt": "PowerPoint 에서 열고 .pptx 로 저장하세요",
    ".xls": "Excel 에서 열고 .xlsx 로 저장하세요",
    ".hwt": "한글 서식 파일입니다. 내용이 든 .hwpx 문서를 넣으세요",
    ".zip": "압축을 풀고 안의 문서를 한 건씩 넣으세요",
}

# 확장자 → 파서 함수 분기표 (새 형식은 여기에 한 줄 추가)
HANDLERS = {
    ".docx": parse_docx,
    ".pdf": parse_pdf,
    ".hwpx": parse_hwpx,
    ".xlsx": parse_xlsx,
    ".pptx": parse_pptx,
}


# 로컬 파싱 입구: 확장자로 파서를 골라 실행하고, 실패 상황을 안내 메시지로 바꿈
def parse_local(path: str | Path) -> ParsedDoc | None:
    from app.core.exceptions import ValidationFailed               # 입력 검증 실패 예외

    p = Path(path)                                                 # 문자열이 와도 Path로
    ext = p.suffix.lower()                                         # 확장자 (소문자)

    handler = HANDLERS.get(ext)                                    # 분기표에서 파서 찾기
    if handler is parse_pdf and pdf_tables_on():                   # PDF이고 PDF_TABLES가 켜져 있으면
        handler = parse_pdf_tables                                 # 표 분리 파서로 교체
    if handler is None:                                            # 지원하지 않는 확장자면
        if ext in _CONVERT_HINT:                                   # 변환하면 되는 형식이면
            raise ValidationFailed(
                f"읽을 수 없는 형식입니다: {ext}",
                detail=_CONVERT_HINT[ext],                         # 변환 방법 안내
            )
        raise ValidationFailed(
            f"지원하지 않는 형식입니다: {ext}",
            detail="핸들러를 추가하면 지원할 수 있습니다",
        )

    try:
        doc = handler(p)                                           # 파싱 실행
    except Exception as exc:                                       # 파서 내부 오류(손상 파일 등)는
        log.warning("로컬 파싱 실패 (%s): %s", p.name, exc)         # 로그만 남기고
        return None                                                # None 반환 (호출 쪽에서 판단)

    if not doc.blocks:                                             # 읽었는데 글자가 하나도 없으면
        raise ValidationFailed(
            f"문서에서 글자를 찾지 못했습니다: {p.name}",
            detail="스캔본(이미지)일 수 있습니다. .env 의 UPSTAGE_PARSE_OCR 를 force 로 "
                   "두고 실동작 모드로 다시 적재해 보세요",          # 상용 OCR 안내
        )

    return doc                                                     # 성공

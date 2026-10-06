from __future__ import annotations

from pathlib import Path                                          # 파일 경로를 객체로 다루기

from app.core.logging import get_logger                           # 로거 생성 함수
from app.integrations.ports import ParsedBlock, ParsedDoc         # 파서 결과 형식 (블록 하나 / 문서 전체)
from app.rag.local_parsers import parse_local                                  # docx/pdf/hwpx/xlsx/pptx 로컬 파서 입구

log = get_logger(__name__)                                        # 이 모듈 전용 로거

_PLAIN = {".txt", ".md"}                                          # 파싱 불필요. 파일 열어 바로 읽기

_HTML = {".html", ".htm"}                                         # 태그를 걷어내야 글자가 남는 형식

_LOCAL_ONLY = {".hwp", ".hwpx"}                                   # 상용 파서에 보내지 않을 형식 (업스테이지 미지원)


# 파일 한 건을 읽어 형식과 무관한 한 가지 모양(ParsedDoc)으로 반환하는 함수
def parse(path: str | Path, *, use_upstage: bool = False) -> ParsedDoc | None:   # None: 로컬 파서 내부 오류 (parse_local과 같은 약속)
    p = Path(path)                                                # 문자열이 와도 Path로
    ext = p.suffix.lower()                                        # 확장자 (소문자)

    if ext in _PLAIN:                                             # txt, md면
        return _parse_plain(p)                                    # 텍스트 파서
    if ext in _HTML:                                              # html이면
        return _parse_html(p)                                     # HTML 파서
    if use_upstage and ext not in _LOCAL_ONLY:                    # 상용 파서를 쓰기로 했고 한글 파일이 아니면
        from app.integrations.upstage import UpstageParser        # 쓸 때만 import (httpx 등 의존성)

        return UpstageParser().parse(str(p))                      # 업스테이지로 파싱
    return parse_local(p)                                         # 나머지는 로컬 파서


# txt: 빈 줄(\n\n) 기준 단락 하나 = 블록 하나 (md는 제목 기준 파서로 넘김)
def _parse_plain(p: Path) -> ParsedDoc:
    if p.suffix.lower() == ".md":                                 # 마크다운이면
        return _parse_markdown(p)                                 # 제목(#) 단위로 나누는 파서로
    text = _read_text(p)                                          # 인코딩을 맞춰 읽기
    blocks = [
        ParsedBlock("조항", f"{p.name} · {i + 1}단락", part.strip())   # 위치 = 파일명 · N단락
        for i, part in enumerate(text.split("\n\n"))              # 빈 줄로 나눈 단락마다
        if part.strip()                                           # 빈 단락은 제외
    ]
    return ParsedDoc(blocks=blocks, page_count=1, table_count=0)  # 쪽 1, 표 없음


# 텍스트 파일을 인코딩 순서대로 시도해 읽기: UTF-8(BOM 포함) → CP949(윈도우 한글) → 깨진 글자 대체
def _read_text(p: Path) -> str:
    raw = p.read_bytes()                                          # 바이트 그대로 읽기
    for enc in ("utf-8-sig", "cp949"):                            # 시도할 인코딩 순서
        try:
            text = raw.decode(enc)                                # 이 인코딩으로 해석
        except UnicodeDecodeError:                                # 안 맞으면
            continue                                              # 다음 인코딩
        if enc != "utf-8-sig":                                    # UTF-8이 아니었으면
            log.info("인코딩을 %s 로 읽었습니다: %s", enc, p.name)   # 기록
        return text                                               # 성공
    log.warning("인코딩을 알 수 없어 글자를 바꿔 읽었습니다: %s", p.name)   # 둘 다 실패
    return raw.decode("utf-8", errors="replace")                  # 깨진 글자는 대체 문자(�)로


# md: 제목(#) 줄을 경계로 자르고, 그 제목을 아래 본문 블록의 위치(locator)로 사용
def _parse_markdown(p: Path) -> ParsedDoc:
    import re                                                     # 제목 줄 판별용

    text = _read_text(p)                                          # 인코딩을 맞춰 읽기
    blocks: list[ParsedBlock] = []                                # 결과 블록 목록
    locator = p.name                                              # 첫 제목 전까지의 위치 = 파일 이름
    buffer: list[str] = []                                        # 현재 제목 아래 모으는 본문 줄

    # 모아 둔 본문을 블록 하나로 저장하고 비우기
    def flush() -> None:
        body = "\n".join(buffer).strip()                          # 줄을 이어 붙임
        if body:                                                  # 내용이 있으면
            blocks.append(ParsedBlock("조항", locator, body))      # 현재 제목을 위치로 블록 추가
        buffer.clear()                                            # 비우기 (리스트를 새로 만들지 않아 nonlocal 불필요)

    for line in text.split("\n"):                                 # 한 줄씩
        if re.match(r"#{1,6}\s", line):                           # '# ' ~ '###### ' 로 시작하는 제목 줄이면
            flush()                                               # 이전 제목의 본문을 먼저 저장
            locator = line.lstrip("#").strip()                    # 새 위치 = '#' 뗀 제목 글자
        else:                                                     # 본문 줄이면
            buffer.append(line)                                   # 모으기
    flush()                                                       # 마지막 제목의 본문 저장
    return ParsedDoc(blocks=blocks, page_count=1, table_count=0)  # 쪽 1, 표 없음


# html: head/script/style 제거 → 표를 떼어 두고 → 본문과 표를 각각 블록으로
def _parse_html(p: Path) -> ParsedDoc:
    import re                                                     # 태그 제거용 정규식

    raw = _read_text(p)                                           # 인코딩을 맞춰 읽기
    raw = re.sub(r"<head.*?</head>", " ", raw, flags=re.S | re.I)   # <head> 통째로 제거 (title 등 본문 아닌 것)
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)   # 스크립트·스타일 제거 (re.S: 줄바꿈 포함, re.I: 대소문자 무시)

    tables = re.findall(r"<table.*?</table>", raw, flags=re.S | re.I)   # 표 부분만 모으기
    body = re.sub(r"<table.*?</table>", " ", raw, flags=re.S | re.I)    # 본문에서는 표 빼기
    body = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()   # 남은 태그 → 공백, 연속 공백 → 하나

    blocks = [ParsedBlock("조항", p.name, body)] if body else []   # 본문이 있으면 첫 블록
    for i, table in enumerate(tables, 1):                         # 표마다 1번부터
        cleaned = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", table)).strip()   # 표 안 태그 제거
        blocks.append(ParsedBlock("표", f"{p.name} · 표{i}", cleaned))   # 표 블록 추가
    return ParsedDoc(blocks=blocks, page_count=1, table_count=len(tables))   # 쪽 1, 표 수

from __future__ import annotations

import re                                   # 정규식 (조/별표/장·절 찾기)
from dataclasses import dataclass           # 간단한 데이터 클래스 만들기

from langchain_text_splitters import RecursiveCharacterTextSplitter   # 긴 텍스트를 길이 기준으로 자르는 도구

from app.integrations.ports import ParsedDoc   # 파서가 돌려주는 문서 (blocks 목록을 가짐)

# 조 머리: 줄 맨 앞의 '제1조(목적)', '제5조의2(정의)' — 괄호 제목까지 있어야 함
#   줄 맨 앞(^, re.M) + 괄호 필수 → 본문 속 '제9조에 따라' 같은 언급은 안 잡힘
_ARTICLE = re.compile(r'^[ \t]*(제\s*\d+\s*조(?:의\s*\d+)?\s*\([^)\n]{1,30}\))', re.M)
# 별표: 별표1, 별표 2 ...
_ANNEX = re.compile(r'(별표\s*\d+)')
# 장, 절, 부칙 제목 줄 (예: '제1장 총칙', '제2절', '부칙') — 줄 전체가 제목이어야 함
_HEADING = re.compile(r'^[ \t]*(?:(제\s*\d+\s*장)|(제\s*\d+\s*절)|(부\s*칙))(?:[ \t]+[^\n]{1,30})?[ \t]*$')
# 별표, 서식 제목 줄 (예: '[별표 1]', '[별지 제1호 서식]')
_ANNEX_HEAD = re.compile(r'^[ \t]*\[(별표\s*\d+|별지[^\]]{0,20})\]')

MAX_CHARS = 1200     # 청크 하나의 최대 글자 수
MIN_CHARS = 30       # 첫 조 앞의 머리말이 이보다 짧으면 버림
TOC_BODY_MIN = 10    # 제목 뒤 내용이 이보다 짧으면 목차 줄로 봄


# 청크 하나 (DB에 넣기 전 초안)
@dataclass
class ChunkDraft:
    kind: str       # 조항 | 표
    locator: str    # 출처 위치 (예: '제2장 제7조(숙박비)', '표3')
    text: str       # 청크 본문


# 텍스트를 조 단위로 자르기 → [(조 제목, 제목+본문), ...]
def _split_articles(text: str) -> list[tuple[str, str]]:
    parts = _ARTICLE.split(text)                 # 캡처 그룹 덕분에 [머리, 제목1, 본문1, 제목2, 본문2, ...]
    if len(parts) <= 1:                          # 조 머리가 하나도 없으면
        return [('', text.strip())] if text.strip() else []   # 전체를 제목 없는 한 덩어리로 (빈 문자열이면 없음)

    out: list[tuple[str, str]] = []
    head = parts[0].strip()                      # 첫 조 앞의 머리말
    if len(head) >= MIN_CHARS:                   # 충분히 길 때만
        out.append(('', head))                   # 제목 없는 덩어리로 보관
    for i in range(1, len(parts), 2):            # 홀수 칸 = 조 제목
        title = parts[i].strip()                                      # 조 제목
        body = parts[i + 1].strip() if i + 1 < len(parts) else ''     # 바로 뒤 짝수 칸 = 본문
        out.append((title, f'{title} {body}'.strip()))                # 본문 앞에 제목을 붙여서 저장
    return out


# 장, 절 제목 줄에서 끊고 그 줄은 본문에서 제외시키기 → [(위치, 본문), ...]
# where: 현재 위치 {'chapter': 장, 'section': 절, 'at': 표시용 위치}. 호출 사이에 이어서 쓰도록 바깥에서 넘겨받음
def _split_headings(text: str, where: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []              # 결과
    lines: list[str] = []                        # 현재 구간에 모으는 본문 줄
    for line in text.split('\n'):                # 한 줄씩
        m = _HEADING.match(line)                 # 장/절/부칙 제목 줄인가
        annex = _ANNEX_HEAD.match(line)          # [별표N]/[별지...] 제목 줄인가
        if not m and (not annex):                # 둘 다 아니면 평범한 본문
            lines.append(line)                   # 모으고
            continue                             # 다음 줄로
        if lines:                                # 제목 줄을 만났는데 모아 둔 본문이 있으면
            out.append((where['at'], '\n'.join(lines)))   # 지금까지 구간을 이전 위치로 저장
            lines = []                           # 새 구간 시작
        if annex:                                # 별표/서식 제목이면
            where['chapter'], where['section'] = ('', '')   # 장/절 정보 초기화
            where['at'] = re.sub(r'\s+', ' ', annex.group(1)).strip()   # 위치 = '별표 1' 등 (공백 하나로 정리)
            lines.append(line)                   # 별표 제목 줄은 본문에 남김
            continue
        chapter, section, _ = m.groups()         # 어느 그룹이 잡혔나: 장 / 절 / 부칙
        if chapter:                              # 장이면
            where['chapter'], where['section'] = (re.sub(r'\s+', '', chapter), '')   # 장 갱신('제1장'), 절 초기화
        elif section:                            # 절이면
            where['section'] = re.sub(r'\s+', '', section)   # 절만 갱신('제2절')
        else:                                    # 부칙이면
            where['chapter'], where['section'] = ('부칙', '')
        where['at'] = ' '.join((x for x in (where['chapter'], where['section']) if x))   # 위치 = '제1장 제2절' (빈 값 제외)
        # 장/절 제목 줄 자체는 lines에 넣지 않음 → 본문에서 빠짐
    if lines:                                    # 마지막에 남은 본문
        out.append((where['at'], '\n'.join(lines)))   # 현재 위치로 저장
    return out


# 너무 긴 조를 limit 이하로 나누기 (최후 수단)
def _hard_wrap(text: str, limit: int = MAX_CHARS) -> list[str]:
    if len(text) <= limit:                       # 이미 짧으면
        return [text]                            # 그대로
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=limit,                        # 조각 최대 길이
        chunk_overlap=0,                         # 조각끼리 겹치지 않음
        separators=['\n\n', '\n', '다. ', '. ', ' ', ''],   # 문단 → 줄 → 문장 끝('다. ', '. ') → 공백 → 글자 순으로 자를 곳을 찾음
        keep_separator='end',                    # 구분자('다. ' 등)는 앞 조각 끝에 남김
    )
    return splitter.split_text(text)             # 조각 리스트


# ParsedDoc → 청크 목록으로 변환해서 반환
def chunk(doc: ParsedDoc) -> list[ChunkDraft]:
    out: list[ChunkDraft] = []                   # 최종 결과
    buffer: list[str] = []                       # 표가 나오기 전까지 모아 둔 조항 텍스트
    buffer_locator = ''                          # 모아 둔 텍스트의 첫 위치 (위치 정보가 없을 때 대신 씀)
    where = {'chapter': '', 'section': '', 'at': ''}   # 현재 장/절 위치 (표를 사이에 두고도 이어짐)

    # 모아 둔 조항 텍스트를 조 단위 청크로 바꿔 out에 넣고 비우기
    def flush() -> None:
        nonlocal buffer, buffer_locator          # 바깥 변수를 다시 대입하기 위해
        if not buffer:                           # 모아 둔 게 없으면
            return                               # 할 일 없음
        out.extend(_articles_from('\n'.join(buffer), buffer_locator, where))   # 이어 붙여서 장/절 → 조 단위로 자름
        buffer = []                              # 비우기
        buffer_locator = ''

    for block in doc.blocks:                     # 문서 블록을 순서대로
        if block.kind == '표':                   # 표를 만나면
            flush()                              # 앞에 모아 둔 조항부터 처리하고
            out.append(ChunkDraft('표', block.locator, block.text))   # 표는 통째로 청크 하나
            continue
        if not buffer_locator:                   # 버퍼의 첫 블록이면
            buffer_locator = block.locator       # 그 위치를 기억
        buffer.append(block.text)                # 조항 텍스트 모으기

    flush()                                      # 마지막에 남은 것 처리
    return out


# 조항 텍스트 덩어리 → 조 단위 ChunkDraft 목록
def _articles_from(text: str, fallback_locator: str, where: dict) -> list[ChunkDraft]:
    drafts: list[ChunkDraft] = []
    # 장/절로 먼저 자르고, 각 구간을 다시 조로 자름 → [(장절 위치, 조 제목, 제목+본문), ...]
    items = [(at, title, body) for at, part in _split_headings(text, where) for title, body in _split_articles(part)]
    for at, title, body in items:
        if not body.strip():                     # 빈 덩어리는
            continue                             # 건너뜀

        # 목차 줄 처리: 제목 뒤 내용이 거의 없으면 독립 청크로 만들지 않음
        remainder = body[len(title):].strip() if title else body   # 제목을 뺀 실제 내용
        if not title and '\n' not in body.strip() and _ANNEX_HEAD.match(body):   # '[별표 1]' 제목 한 줄뿐이면
            remainder = ''                       # 내용 없음으로 취급
        if len(remainder) < TOC_BODY_MIN:        # 내용이 너무 짧으면
            if drafts:                           # 앞 청크가 있으면
                drafts[-1].text += '\n' + body   # 거기에 이어 붙이고
            else:                                # 없으면
                drafts.append(ChunkDraft('조항', at or fallback_locator, body))   # 장절 위치(없으면 블록 위치)로 새 청크
            continue

        # 위치 정하기: '장 절 조', 별표가 있으면 뒤에 ' · 별표N'
        if not title:                            # 제목 없는 덩어리(머리말 등)
            locator = at or fallback_locator     # 장절 위치, 없으면 블록 위치
        else:
            annex = _ANNEX.search(body)          # 본문에서 별표 찾기
            locator = f'{at} {title}'.strip()    # 예: '제2장 제7조(숙박비)'
            locator = locator if not annex else f'{locator} · {annex.group(1)}'   # 예: '... · 별표1'

        # 너무 길면 잘라서 ' (1/3)', ' (2/3)' ... 꼬리표 붙이기
        pieces = _hard_wrap(body)
        for i, piece in enumerate(pieces):
            suffix = f' ({i + 1}/{len(pieces)})' if len(pieces) > 1 else ''   # 조각이 하나면 꼬리표 없음
            drafts.append(ChunkDraft('조항', f'{locator}{suffix}', piece))
    return drafts


# 요약 문구 생성
def summarize(chunks: list[ChunkDraft]) -> str:
    articles = sum((1 for c in chunks if c.kind == '조항'))   # 조항 청크 수
    tables = sum((1 for c in chunks if c.kind == '표'))       # 표 청크 수
    return f'조항 단위 {articles} + 표 단위 {tables} = {len(chunks)} 청크'

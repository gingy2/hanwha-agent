"""KURE-v1 · bge-m3 두 임베딩 모델로 문장 쌍의 코사인 유사도를 비교한다."""
import os
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"                       # 인터넷 안 타고 로컬 모델만 사용 (import 전에)

MODELS = Path(__file__).resolve().parents[4] / "models"  # hanwha-agent 바로 옆 models/
KURE = MODELS / "KURE-v1"                                # 한국어 특화 임베딩 모델
BGE = MODELS / "bge-m3"                                  # 다국어 임베딩 모델

PAIRS = [
    ("광역시 숙박비 상한", "잠자리 비용 한도", "같은 뜻"),
    ("출장 전에 신청서를 낸다", "출장은 사전 신청이 원칙이다", "같은 뜻"),
    ("법인카드로 결제한다", "법인카드 사용 지침을 따른다", "가까움"),
    ("일비는 하루 단위로 준다", "숙박비는 1박 단위로 준다", "가까움"),
    ("출장 신청서를 낸다", "재택근무를 신청한다", "다름"),
    ("숙박비 상한액", "정보보안 지침 위반", "남남"),
]

def main()->None:
    if not (KURE.is_dir() and BGE.is_dir()):
        print('모델 폴더 찾지 못함. 경로 검토 바람.')
        print(f'{KURE}')
        print(f'{BGE}')
        return

    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim

    sents=[s for a,b,_ in PAIRS for s in (a,b)]
    for name,path in (('KURE-v1',KURE),('bge-m3',BGE)):
        model=SentenceTransformer(str(path))
        v=model.encode(sents,normalize_embeddings=True)
        print(f'[{name}] 차원 {model.get_embedding_dimension()}-모양{v.shape}')
        for i, (a,b,label) in enumerate(PAIRS):
            score=float(cos_sim(v[i*2],v[i*2+1]))
            print(f'{score:+.4f}{label:4s}{a}/{b}')

if __name__ == '__main__':
    main()
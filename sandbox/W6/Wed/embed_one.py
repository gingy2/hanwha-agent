from __future__ import annotations
import os
from pathlib import Path

os.environ.setdefault('HF_HUB_OFFLINE','1')

from app.core.config import get_settings

QUESTION='국내 출장 숙박비 얼마까지 지원됨?'
HEAD=5   # 상위 5개 확인하겠다

def main()->None:
    folder=Path(get_settings().embed_model_dir)
    if not folder.is_dir():
        print(f'모델 폴더 없음:{folder}')
        print('.env의 EMBED_MODEL_DIR 확인 바람')
        return

    from app.rag import embedder

    vec=embedder.embed_query(QUESTION)
    print('질문:',QUESTION)
    print('길이:',len(vec))
    print('차원:',embedder.embed_dim())
    print('벡터 앞부분:',[round(x,6) for x in vec[:HEAD]])

if __name__=='__main__':
    main()
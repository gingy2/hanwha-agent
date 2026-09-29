"""KURE-v1 · bge-m3 를 프로젝트 폴더 옆 models/ 에 받는다. 끊기면 다시 실행 → 이어 받음."""
from pathlib import Path

from huggingface_hub import snapshot_download

DEST = Path(__file__).resolve().parents[4] / "models"  # hanwha-agent 바로 옆

for repo in ["nlpai-lab/KURE-v1", "BAAI/bge-m3"]:
    # onnx/ 는 같은 가중치 사본(2.27GB)이라 뺀다
    path = snapshot_download(repo, local_dir=DEST / repo.split("/")[1], ignore_patterns=["onnx/*"])
    print("v", path)

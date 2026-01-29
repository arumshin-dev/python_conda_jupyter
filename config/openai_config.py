import os
from pathlib import Path
from dotenv import load_dotenv

def find_env_file(start_path: Path) -> Path:
    """Search upwards from start_path for a .env file.
    Returns the Path to the .env file if found, otherwise raises FileNotFoundError.
    """
    current = start_path.resolve()
    for _ in range(10):  # look up to 10 levels up
        candidate = current / ".env"
        if candidate.is_file():
            return candidate
        if current.parent == current:
            break
        current = current.parent
    raise FileNotFoundError("🔴 .env 파일을 찾을 수 없습니다. 프로젝트 루트에 .env 를 배치하세요.")

# Determine the directory of this file and locate .env in the project root
BASE_DIR = Path(__file__).resolve().parent
env_path = find_env_file(BASE_DIR)
load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("🔴 OPENAI_API_KEY 가 .env 파일에 없어요. 파일을 확인하세요.")


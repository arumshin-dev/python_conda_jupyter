"""
🎯 FastAPI 실습: OpenAI Whisper를 활용한 음성-텍스트 변환: Speech-to-Text (STT)
1. Lifespan을 활용한 Whisper 모델 로딩
2. UploadFile을 사용한 오디오 파일 업로드 처리
3. 임시 파일(tempfile) 생성 및 정리 패턴 이해
4. 음성 인식 결과에서 텍스트와 언어 감지 추출

📌 사전 준비:
1. 시스템에 ffmpeg 설치
   - Mac: brew install ffmpeg
   - Ubuntu: apt install ffmpeg
   - Windows: ffmpeg 다운로드 후 Path 설정
2. pip install openai-whisper python-multipart

📌 실행 방법:
python ./lab2/speech_to_text.py
"""

from fastapi import FastAPI, UploadFile, File
from contextlib import asynccontextmanager
import whisper                  # https://pypi.org/project/openai-whisper/
import shutil,os, tempfile

# 전역 모델 변수
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("====== 모델 로딩중 ....")
    # 'base' 모델은 가볍고 빠름 (정확도를 높이려면 'small', 'medium' 사용)
    ml_models["whisper"] = whisper.load_model("base")
    print("✅ 모델 로딩 완료!")
    yield
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # 1. 업로드된 파일을 임시 파일로 저장 (Whisper는 파일 경로를 요구함)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        # 2. 모델 가져오기 및 추론
        model = ml_models["whisper"]

        # 3. Transcribe 실행 (로컬 CPU/GPU 사용)
        result = model.transcribe(temp_path)

        return {
            "filename": file.filename,
            "text": result["text"],
            "language": result["language"]
        }
    
    finally:
        # 4. 처리가 끝나면 임시 파일 삭제 (청소)
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
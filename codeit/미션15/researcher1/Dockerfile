# 1. Python 이미지
FROM python:3.10-slim

# 2. 작업 디렉토리
WORKDIR /app

# 3. requirements 복사 & 설치-캐시 없이 설치하여 이미지 경량화
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 및 데이터 복사
# COPY train.py train.csv ./
COPY train.py .
COPY train.csv .
COPY test.csv .

# 5. 모델 저장 디렉토리 생성
RUN mkdir -p /app/output

# 6. 학습 실행
CMD ["python", "train.py"]


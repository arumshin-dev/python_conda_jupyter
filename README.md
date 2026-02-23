# Data Science & AI Study

이 저장소는 데이터 사이언스, 머신러닝, 딥러닝 공부를 위한 코드와 노트를 담고 있습니다.
Streamlit을 활용한 웹 애플리케이션과 주피터 노트북을 통한 데이터 분석 예제들이 포함되어 있습니다.

## 📂 프로젝트 구조

- `app.py`: Streamlit 앱의 메인 진입점
- `pages/`: Streamlit 멀티 페이지 앱을 위한 페이지 파일들
  - 이미지 분류, OCR 등 다양한 기능이 구현되어 있습니다.
- `utils.py`: 공통적으로 사용되는 함수 및 모델 로딩 로직
- `*.ipynb`: 데이터 분석 및 머신러닝 학습을 위한 주피터 노트북 파일들

## 🛠 사용 기술

- **Web Framework**: Streamlit, FastAPI
- **Data Science**: Pandas, NumPy, Plotly
- **Deep Learning**: PyTorch, Transformers (Hugging Face)
- **Vision**: OpenCV, EasyOCR, Pillow

## 🚀 실행 방법

### 1. 환경 설정

필요한 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

### 2. 앱 실행

Streamlit 앱을 실행합니다.

```bash
streamlit run app.py
```

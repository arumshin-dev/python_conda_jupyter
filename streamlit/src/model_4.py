#####################################################################
# FastAPI 서버가 될 부분
#####################################################################

import random

class MyModel:
    def __init__(self):
        # 실제 모델이라면 여기서 가중치를 로드합니다.
        print("Model initialized")

    def predict(self, input_text):
        # AI 예측 로직 시뮬레이션
        # 나중에 이 부분만 FastAPI의 엔드포인트 함수로 변경하면 됩니다.
        prediction_score = random.random()
        return {
            "input": input_text,
            "score": prediction_score,
            "is_spam": prediction_score > 0.5
        }
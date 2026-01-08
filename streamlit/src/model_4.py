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
        banned = ["광고", "무료", "당첨"]
        if any(word in input_text for word in banned):
            return {"input": input_text,
                    "is_spam": True, 
                    "score": 1.0}
        else:
            return {"input": input_text,
                    "is_spam": False, 
                    "score": 0.0}

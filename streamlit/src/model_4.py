#####################################################################
# FastAPI 서버가 될 부분
#####################################################################

import random

class MyModel:
    def __init__(self):
        # 실제 모델이라면 여기서 가중치를 로드합니다.
        print("Model initialized")# ✅ 캐싱 확인용

    def predict(self, input_text, keywords):
        # AI 예측 로직 시뮬레이션
        # 나중에 이 부분만 FastAPI의 엔드포인트 함수로 변경하면 됩니다.
        if any(word in input_text for word in keywords):
            return {"input": input_text,
                    "is_spam": True, 
                    "score": 1.0,
                    "reason": "금지어가 포함되어 있습니다."
                    }
        else:
            return {"input": input_text,
                    "is_spam": False, 
                    "score": 0.0,
                    "reason": "특이사항 없음"
                    }

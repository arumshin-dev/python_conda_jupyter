# scripts/test_openai_key.py (맨 위)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.openai_config import OPENAI_API_KEY
print('🔑 API key loaded successfully' if OPENAI_API_KEY else '❌ No API key')


from openai import OpenAI

def check_openai_key_and_models():
    """
    1. OpenAI API Key가 유효한지 확인
    2. 현재 계정에서 사용 가능한 모델 목록 반환
    """
    try:
        client = OpenAI()  # 환경변수 OPENAI_API_KEY 사용

        # 🔹 모델 목록 조회 (가장 확실한 키 검증 방법)
        models = client.models.list()

        model_ids = sorted([m.id for m in models.data])

        return {
            "valid": True,
            "model_count": len(model_ids),
            "models": model_ids
        }

    except Exception as e:
        msg = str(e).lower()

        if "authentication" in msg or "api key" in msg:
            return {"valid": False, "error": "❌ API 키 인증 실패"}
        elif "permission" in msg:
            return {"valid": False, "error": "❌ 모델 접근 권한 없음"}
        elif "rate limit" in msg:
            return {"valid": True, "warning": "⚠️ 사용량 한도 초과"}
        else:
            return {"valid": False, "error": f"❌ 알 수 없는 오류: {e}"}

result = check_openai_key_and_models()

if result["valid"]:
    print("✅ OpenAI API Key 사용 가능")
    print(f"📦 사용 가능한 모델 수: {result['model_count']}")
    print("🔍 모델 목록:")
    for m in result["models"]:
        print(" -", m)
else:
    print(result["error"])

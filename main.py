# your-fastapi-project/main.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import List, Dict

# 분리된 파일들에서 필요한 것들을 import 합니다.
from models import SimpleChatRequest, ConversationRequest, ChatResponse, Message
from auth import router as auth_router, get_current_user, UserInDB # auth.py에서 라우터와 함수/모델 import

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(title="부트캠프 ChatGPT API 서버", version="1.0.0")

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 부트캠프 API 엔드포인트 URL (이 부분은 main.py에 유지하거나 config.py로 분리할 수 있습니다)
BOOTCAMP_API_URL = "https://dev.wenivops.co.kr/services/openai-api"

# auth.py에서 정의된 라우터를 FastAPI 앱에 포함
app.include_router(auth_router) # auth_router에 정의된 /token, /register 엔드포인트가 추가됩니다.

# GET 요청: 서버 상태 확인 (기존과 동일)
@app.get("/")
async def root():
    return {"message": "부트캠프 ChatGPT API 서버가 실행 중입니다"}

# --- 채팅 관련 엔드포인트

# 채팅 API 호출 헬퍼 함수
async def call_bootcamp_api(messages: List[Dict]) -> Dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                BOOTCAMP_API_URL,
                json=messages,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=408, detail="API 요청 시간이 초과되었습니다")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"API 오류: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.post("/chat/simple", response_model=ChatResponse, summary="간단한 채팅 (단일 메시지)")
async def simple_chat(request: SimpleChatRequest, current_user: UserInDB = Depends(get_current_user)):
    messages = [
        {"role": "system", "content": request.system_message},
        {"role": "user", "content": request.message}
    ]
    response_data = await call_bootcamp_api(messages)
    ai_message = response_data["choices"][0]["message"]["content"]
    usage_info = response_data["usage"]
    return ChatResponse(response=ai_message, usage=usage_info)

@app.post("/chat/conversation", response_model=ChatResponse, summary="대화 맥락 유지 채팅")
async def conversation_chat(request: ConversationRequest, current_user: UserInDB = Depends(get_current_user)):
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    if not any(msg["role"] == "system" for msg in messages):
        messages.insert(0, {"role": "system", "content": "You are a helpful assistant."})

    response_data = await call_bootcamp_api(messages)
    ai_message = response_data["choices"][0]["message"]["content"]
    usage_info = response_data["usage"]
    return ChatResponse(response=ai_message, usage=usage_info)

@app.post("/chat/role", summary="특정 역할을 가진 AI와 채팅")
async def role_based_chat(role: str, message: str, current_user: UserInDB = Depends(get_current_user)):
    if role == "시인":
        system_message = "assistant는 시인이다. 모든 답변을 아름다운 시의 형태로 표현한다."
    elif role == "파이썬 선생님":
        system_message = "assistant는 친절한 파이썬 알고리즘의 힌트를 주는 선생님이다."
    elif role == "요리사":
        system_message = "assistant는 경험이 풍부한 요리사다. 맛있는 요리법을 알려준다."
    else:
        system_message = f"assistant는 {role}이다."

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": message}
    ]
    response_data = await call_bootcamp_api(messages)
    return {
        "role": role,
        "user_message": message,
        "ai_response": response_data["choices"][0]["message"]["content"],
        "usage": response_data["usage"]
    }

# 서버 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
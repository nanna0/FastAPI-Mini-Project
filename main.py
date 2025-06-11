# your-fastapi-project/main.py (변경된 부분 없음, 기존 코드를 그대로 사용)

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
from typing import List, Dict
from dotenv import load_dotenv
import os
from collections import defaultdict

# 분리된 파일들에서 필요한 것들을 import 합니다.
from models import SimpleChatRequest, ConversationRequest, ChatResponse, Message, ChatMessage, ChatHistoryResponse
from auth import router as auth_router, get_current_user, UserInDB

load_dotenv()

app = FastAPI(title="부트캠프 ChatGPT API 서버", version="1.0.0")

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
app.mount("/static", StaticFiles(directory="static"), name="static") # static 파일 연결

BOOTCAMP_API_URL = os.getenv("BOOTCAMP_API_URL", "https://dev.wenivops.co.kr/services/openai-api")

app.include_router(auth_router)

# --- 채팅 기록을 위한 임시 인메모리 저장소 ---
fake_chat_db: Dict[str, List[ChatMessage]] = defaultdict(list)


@app.get("/", summary="서버 상태 확인")
async def root():
    from fastapi.responses import FileResponse
    return {"message": "부트캠프 ChatGPT API 서버가 실행 중입니다"}

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

# --- 새로운 채팅 기록 엔드포인트 ---

# 채팅 기록 저장 엔드포인트
@app.post("/chat/save", status_code=status.HTTP_201_CREATED, summary="채팅 기록 저장")
async def save_chat_message(chat_message: ChatMessage, current_user: UserInDB = Depends(get_current_user)):
    if chat_message.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="메시지를 저장할 권한이 없습니다."
        )
    fake_chat_db[current_user.username].append(chat_message)
    return {"message": "채팅 메시지가 저장되었습니다."}

# 사용자별 채팅 기록 조회 엔드포인트
@app.get("/chat/history", response_model=ChatHistoryResponse, summary="사용자별 채팅 기록 조회")
async def get_chat_history(current_user: UserInDB = Depends(get_current_user)):
    history = fake_chat_db[current_user.username]
    return {"history": history}

# --- 기존 채팅 엔드포인트 (채팅 기록 저장 로직은 이 곳에서만 담당) ---

@app.post("/chat/simple", response_model=ChatResponse, summary="간단한 채팅 (단일 메시지)")
async def simple_chat(request: SimpleChatRequest, current_user: UserInDB = Depends(get_current_user)):
    user_message = Message(role="user", content=request.message)
    system_message_obj = Message(role="system", content=request.system_message)
    messages_for_api = [
        {"role": system_message_obj.role, "content": system_message_obj.content},
        {"role": user_message.role, "content": user_message.content}
    ]

    response_data = await call_bootcamp_api(messages_for_api)
    ai_response_content = response_data["choices"][0]["message"]["content"]
    usage_info = response_data["usage"]

    ai_message = Message(role="assistant", content=ai_response_content)

    # --- 채팅 기록 저장: 백엔드에서만 저장 로직 실행 ---
    # 사용자 메시지 저장
    await save_chat_message(ChatMessage(
        username=current_user.username,
        role=user_message.role,
        content=user_message.content
    ), current_user=current_user)

    # AI 응답 메시지 저장
    await save_chat_message(ChatMessage(
        username=current_user.username,
        role=ai_message.role,
        content=ai_message.content
    ), current_user=current_user)
    # --- 저장 로직 끝 ---

    return ChatResponse(response=ai_response_content, usage=usage_info)


@app.post("/chat/conversation", response_model=ChatResponse, summary="대화 맥락 유지 채팅")
async def conversation_chat(request: ConversationRequest, current_user: UserInDB = Depends(get_current_user)):
    messages_for_api = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    if not any(msg["role"] == "system" for msg in messages_for_api):
        messages_for_api.insert(0, {"role": "system", "content": "You are a helpful assistant."})

    response_data = await call_bootcamp_api(messages_for_api)
    ai_response_content = response_data["choices"][0]["message"]["content"]
    usage_info = response_data["usage"]

    # --- 채팅 기록 저장: 백엔드에서만 저장 로직 실행 ---
    # 전송된 모든 메시지 저장 (conversation의 경우, 프론트엔드에서 보낸 모든 메시지를 저장)
    for msg in request.messages:
        await save_chat_message(ChatMessage(
            username=current_user.username,
            role=msg.role,
            content=msg.content
        ), current_user=current_user)

    # AI 응답 메시지 저장
    await save_chat_message(ChatMessage(
        username=current_user.username,
        role="assistant",
        content=ai_response_content
    ), current_user=current_user)
    # --- 저장 로직 끝 ---

    return ChatResponse(response=ai_response_content, usage=usage_info)


@app.post("/chat/role", summary="특정 역할을 가진 AI와 채팅")
async def role_based_chat(role: str, message: str, current_user: UserInDB = Depends(get_current_user)):
    if role == "시인":
        system_message_content = "assistant는 시인이다. 모든 답변을 아름다운 시의 형태로 표현한다."
    elif role == "파이썬 선생님":
        system_message_content = "assistant는 친절한 파이썬 알고리즘의 힌트를 주는 선생님이다."
    elif role == "요리사":
        system_message_content = "assistant는 경험이 풍부한 요리사다. 맛있는 요리법을 알려준다."
    else:
        system_message_content = f"assistant는 {role}이다."

    user_message_obj = Message(role="user", content=message)
    system_message_obj = Message(role="system", content=system_message_content)

    messages_for_api = [
        {"role": system_message_obj.role, "content": system_message_obj.content},
        {"role": user_message_obj.role, "content": user_message_obj.content}
    ]

    response_data = await call_bootcamp_api(messages_for_api)
    ai_response_content = response_data["choices"][0]["message"]["content"]
    usage_info = response_data["usage"]

    # --- 채팅 기록 저장: 백엔드에서만 저장 로직 실행 ---
    # 사용자 메시지 저장
    await save_chat_message(ChatMessage(
        username=current_user.username,
        role=user_message_obj.role,
        content=user_message_obj.content
    ), current_user=current_user)

    # AI 응답 메시지 저장
    await save_chat_message(ChatMessage(
        username=current_user.username,
        role="assistant",
        content=ai_response_content
    ), current_user=current_user)
    # --- 저장 로직 끝 ---

    return {
        "role": role,
        "user_message": message,
        "ai_response": ai_response_content,
        "usage": usage_info
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
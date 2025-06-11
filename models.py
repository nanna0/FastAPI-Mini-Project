# your-fastapi-project/models.py

from pydantic import BaseModel
from typing import List, Dict, Union
from datetime import datetime

# 사용자 관련 모델
class UserInDB(BaseModel):
    username: str
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str 

# 인증(토큰) 관련 모델
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

# 채팅 관련 모델
class Message(BaseModel):
    role: str
    content: str

class SimpleChatRequest(BaseModel):
    message: str
    system_message: str = "You are a helpful assistant."

class ConversationRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    response: str
    usage: Dict

# 채팅 기록 모델
class ChatMessage(BaseModel):
    username: str
    role: str
    content: str
    timestamp: datetime = datetime.now() # 채팅 시간 기록 (메세지 생성된 시간)

class ChatHistoryResponse(BaseModel):
    history: List[ChatMessage] # ChatMessage 객체의 리스트
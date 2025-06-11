# 필요한 라이브러리들을 가져옵니다
from fastapi import FastAPI, HTTPException, Depends, status # FastAPI 프레임워크와 예외처리, 의존성 주입, 상태 코드
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # OAuth2PasswordBearer (JWT 스키마), 로그인 폼
from pydantic import BaseModel, EmailStr # 데이터 검증을 위한 모델 생성 (EmailStr 추가)
import httpx  # HTTP 요청을 보내기 위한 라이브러리
from typing import List, Dict, Union # 타입 힌트를 위한 라이브러리
from datetime import datetime, timedelta # 토큰 만료 시간 관리를 위한 라이브러리
from jose import JWTError, jwt # JWT 생성 및 검증
from passlib.context import CryptContext # 비밀번호 해싱

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(title="부트캠프 ChatGPT API 서버", version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware
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
# 부트캠프 API 엔드포인트 URL
BOOTCAMP_API_URL = "https://dev.wenivops.co.kr/services/openai-api"

# --- JWT 관련 설정 ---
SECRET_KEY = "your-super-secret-key" # 실제 프로젝트에서는 환경 변수로 관리
ALGORITHM = "HS256" # JWT 서명 알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 액세스 토큰 만료 시간 (분)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # 비밀번호 해싱 컨텍스트
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # 토큰을 받을 엔드포인트 지정

# 간단한 인메모리 사용자 데이터베이스 (실제로는 DB를 사용)
# 나중에 DB 연동 시 이 부분을 대체
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": pwd_context.hash("testpassword"), # 미리 해싱된 비밀번호
    }
}

# --- Pydantic 모델 (기존 모델에 User, Token 모델 추가) ---

# 사용자 모델 (DB 저장용 - 실제 DB 모델과 유사)
class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: Union[str, None] = None

# 로그인 요청 모델
class Token(BaseModel):
    access_token: str
    token_type: str

# 토큰 데이터 모델 (JWT 페이로드)
class TokenData(BaseModel):
    username: Union[str, None] = None


# 단일 메시지의 구조를 정의
class Message(BaseModel):
    role: str  # "system", "user", "assistant" 중 하나
    content: str  # 메시지 내용

# 간단한 채팅 요청 모델
class SimpleChatRequest(BaseModel):
    message: str  # 사용자 메시지
    system_message: str = "You are a helpful assistant."  # AI 역할 설정 (기본값)

# 전체 대화 요청 모델 (대화 맥락 유지용)
class ConversationRequest(BaseModel):
    messages: List[Message]  # 메시지 목록

# 응답 모델
class ChatResponse(BaseModel):
    response: str  # AI의 응답
    usage: Dict  # 토큰 사용량 정보


# --- 유틸리티 함수 (비밀번호 해싱, JWT 생성/검증) ---

# 비밀번호 검증
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 사용자 가져오기
def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

# 액세스 토큰 생성
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15) # 기본 15분
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 현재 사용자 가져오기 (의존성 주입)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user

# GET 요청: 서버 상태 확인
@app.get("/")
async def root():
    return {"message": "부트캠프 ChatGPT API 서버가 실행 중입니다"}

# 로그인 엔드포인트
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 간단한 채팅 엔드포인트
@app.post("/chat/simple", response_model=ChatResponse)
async def simple_chat(request: SimpleChatRequest, current_user: UserInDB = Depends(get_current_user)):
    """
    간단한 채팅 함수 - 단일 메시지만 전송
    대화 맥락이 유지되지 않음
    """
    # current_user 변수를 통해 현재 로그인한 사용자 정보에 접근할 수 있다.
    # 예: print(f"User {current_user.username} is chatting.")

    # 부트캠프 API 형식에 맞는 메시지 배열 생성
    messages = [
        {"role": "system", "content": request.system_message},  # AI 역할 설정
        {"role": "user", "content": request.message}  # 사용자 메시지
    ]

    # 비동기 HTTP 클라이언트로 API 호출
    async with httpx.AsyncClient() as client:
        try:
            # 부트캠프 API에 POST 요청 보내기
            response = await client.post(
                BOOTCAMP_API_URL,
                json=messages,  # 메시지 배열을 JSON으로 전송
                timeout=30.0  # 30초 타임아웃 설정
            )

            # HTTP 상태 코드 확인 (200이 아니면 예외 발생)
            response.raise_for_status()

            # 응답을 JSON으로 파싱
            response_data = response.json()

            # 응답에서 AI 메시지와 사용량 정보 추출
            ai_message = response_data["choices"][0]["message"]["content"]
            usage_info = response_data["usage"]

            # 결과 반환
            return ChatResponse(
                response=ai_message,
                usage=usage_info
            )

        except httpx.TimeoutException:
            # 요청 시간 초과
            raise HTTPException(status_code=408, detail="API 요청 시간이 초과되었습니다")
        except httpx.HTTPStatusError as e:
            # HTTP 오류 (4xx, 5xx)
            raise HTTPException(status_code=e.response.status_code, detail=f"API 오류: {e}")
        except Exception as e:
            # 기타 예외
            raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# 대화 맥락을 유지하는 채팅 엔드포인트
@app.post("/chat/conversation", response_model=ChatResponse)
async def conversation_chat(request: ConversationRequest, current_user: UserInDB = Depends(get_current_user)):
    """
    대화 맥락을 유지하는 채팅 함수
    이전 대화 내역을 모두 포함해서 전송
    """

    # 메시지 배열을 딕셔너리 형태로 변환
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    # system 메시지가 없으면 기본값 추가
    if not any(msg["role"] == "system" for msg in messages):
        messages.insert(0, {"role": "system", "content": "You are a helpful assistant."})

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                BOOTCAMP_API_URL,
                json=messages,
                timeout=30.0
            )

            response.raise_for_status()
            response_data = response.json()

            ai_message = response_data["choices"][0]["message"]["content"]
            usage_info = response_data["usage"]

            return ChatResponse(
                response=ai_message,
                usage=usage_info
            )

        except httpx.TimeoutException:
            raise HTTPException(status_code=408, detail="API 요청 시간이 초과되었습니다")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"API 오류: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# 역할 기반 채팅 (시인, 선생님 등)
@app.post("/chat/role")
async def role_based_chat(role: str, message: str, current_user: UserInDB = Depends(get_current_user)):
    """
    특정 역할을 가진 AI와 채팅

    예시:
    - role: "시인", message: "지구는 왜 파란가요?"
    - role: "파이썬 선생님", message: "반복문을 설명해주세요"
    """

    # 역할에 따른 system 메시지 생성
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

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                BOOTCAMP_API_URL,
                json=messages,
                timeout=30.0
            )

            response.raise_for_status()
            response_data = response.json()

            return {
                "role": role,
                "user_message": message,
                "ai_response": response_data["choices"][0]["message"]["content"],
                "usage": response_data["usage"]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# 서버 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


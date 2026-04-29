from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator # field_validator 추가
import re # 정규표현식 사용을 위해 추가
from enum import Enum #리스트를 정해두어 그 중에서 고르도록 함

app = FastAPI()

# --- 데이터 구조 정의 ---

# 1. 기본 경로(Root) 설정
@app.get("/")
def read_root():
    return {"message": "안녕"}

# 2. 테스트용 API 경로 추가
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

#성별 선택지 정의
class Gender(str, Enum):
    male = "남자"
    female = "여자"

#3. 회원가입 데이터구조
class UserCreate(BaseModel):
    email: str
    name: str
    age: int
    gender: Gender 
    password: str

    # 비밀번호 검증 함수 추가
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str):
        # 1. 길이 체크 (8~20자)
        if not (8 <= len(v) <= 20):
            raise ValueError('비밀번호는 8자 이상 20자 이하로 설정해주세요.')
        
        # 2. 영문자 포함 여부 체크
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('비밀번호에 최소 하나의 영문자가 포함되어야 합니다.')
            
        # 3. 숫자 포함 여부 체크
        if not re.search(r'\d', v):
            raise ValueError('비밀번호에 최소 하나의 숫자가 포함되어야 합니다.')
            
        # 4. 허용된 문자만 있는지 체크 (영문+숫자만)
        if not re.fullmatch(r'[A-Za-z\d]+', v):
            raise ValueError('비밀번호는 영문자와 숫자만 사용할 수 있습니다.')
            
        return v

#4. 로그인 시 받을 데이터 규칙
class LoginRequest(BaseModel):
    email: str
    password: str

# 가입된 유저들을 저장할 임시 명단 (서버 끄면 초기화됨)
db_users = [] 
""" 지금은 서버 끄면 초기화지만 나중에 DB에 저장 필요"""



#API
#회원가입 API
@app.post("/signup")
def signup(user: UserCreate):
    # 이미 가입된 이메일인지 확인
    for u in db_users:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    
    # 명단에 추가
    db_users.append(user.dict())
    return {"message": "회원가입 완료!", "user_name": user.name}


#로그인 API
@app.post("/login")
def login(request: LoginRequest):
    for u in db_users:
        if u["email"] == request.email:
            if u["password"] == request.password:
                return {"message": f"환영합니다, {u['name']}님!", "status": "success"}
            else:
                raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다.")
                
    raise HTTPException(status_code=404, detail="존재하지 않는 아이디입니다.")
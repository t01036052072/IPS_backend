import re
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# 1. database.py에서 설정값들을 가져옵니다
from database import SessionLocal, engine, UserTable, Base

# 서버 시작 시 테이블 생성 (이미 있으면 통과함)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2. DB 연결 세션을 관리하는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 데이터 양식
class UserCreate(BaseModel):
    email: str
    name: str
    age: int
    gender: str
    password: str = Field(..., min_length=8, max_length=20)

@app.get("/")
def read_root():
    return {"message": "의료 AI 백엔드 서버가 작동 중입니다!"}

# 3. [핵심] 회원가입 및 DB 저장 기능
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # [검사] 비밀번호 규칙 확인 (어제 했던 것)
    if not re.search(r"[A-Za-z]", user.password) or not re.search(r"\d", user.password):
        raise HTTPException(status_code=400, detail="비밀번호는 영문+숫자 조합이어야 합니다.")

    # [검사] 중복 이메일 확인
    existing_user = db.query(UserTable).filter(UserTable.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    # [생성] DB에 넣을 유저 객체 만들기
    new_user = UserTable(
        email=user.email,
        name=user.name,
        age=user.age,
        gender=user.gender,
        password=user.password 
    )

    # [저장] DB 장부에 기록하고 확정짓기
    db.add(new_user)     # 장부에 올리기
    db.commit()          # 도장 찍기 (저장 확정)
    db.refresh(new_user) # 저장된 데이터 다시 확인

    return {"message": f"{new_user.name}님, DB에 안전하게 저장되었습니다!", "id": new_user.id}
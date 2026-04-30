from fastapi import FastAPI, HTTPException, File, UploadFile
from schemas import UserCreate, LoginRequest
import shutil
import os
from datetime import datetime
app = FastAPI()


# --- 설정 및 초기화 ---
UPLOAD_DIR = "./uploads"

# 업로드 폴더가 없으면 생성
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
#이게 폴더 만드는 부분인데 모든 사용자의 이미지가 한 번에 저장된느거라 
#개인용으로 DB 분리하는 작업 필요

db_users = [] #가입된 유저들을 저장할 임시 명단 (서버 끄면 초기화됨) 
""" 지금은 서버 끄면 초기화지만 나중에 DB에 저장 필요"""


 # --- 데이터 구조 정의 ---

# 1. 기본 경로(Root) 설정
@app.get("/")
def read_root():
    return {"message": "안녕"}

# 2. 테스트용 API 경로 추가
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}


#----------------API----------------------
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


#의약품 분석 API (이미지 업로드)
#앱에서 보내는 사진을 서버의 하드디스크에 저장하는 과정
@app.post("/pills/analyze")
async def analyze_pill(file: UploadFile = File(...)):
    # 1. 파일 확장자 검사
    extension = file.filename.split(".")[-1].lower()
    if extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="이미지 파일(jpg, png)만 가능합니다.")

    # 2. 유니크한 파일명 생성 (시간_파일명) - 여러 파일들 식별
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    # 3. 서버 로컬 폴더에 저장
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 중 오류 발생: {str(e)}")

    # 4. 결과 반환 (추후 AI 모델 연결 지점)
    return {
        "status": "success",
        "message": "이미지가 업로드되었습니다. 분석을 시작합니다.",
        "saved_path": file_path,
        "ai_result": None  # AI 파트원이 완성하면 여기에 결과값이 들어갑니다.
    }



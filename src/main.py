from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.services.post_service import PostService, get_post_service

app = FastAPI(
    title= "FastAPI NCP Mailing Service",
    description= "게시판과 NCP메일 발송 기능을 제공하는 서비스입니다.",
    version= "1.0.0",
    docs_url= "/docs",
    redoc_url="/redoc"
)


@app.get("/")
def heal_check():
    return {"status": "ok"}


@app.get("/ping")
async def db_ping():
    try:
        with engine.connect() as conn:
            return {"status:" : "DB Connected"  }
    except Exception as e :
        return {"status": "error" , "message": str(e)}


#서버 구동시 자동으로 실행
@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)








#게시글 생성
#response_model - 스웨거문서 활용
@app.post(
        "/posts", 
        response_model = PostResponse,
        summary = "새 게시글 생성",
        description = "새로운 게시글을 생성합니다."
        ) 
def create_post(post:PostCreate, post_service:PostService = Depends(get_post_service)):
    """
    요청받은 post_data (title, content)를 Post 모델에 매핑해 DB에 저장합니다.
    """
    # Pydantic 모델(PostCreate)을 dict로 바꾸고 ORM 모델(Post)에 할당
    new_post = post_service.create_post(post)

    return new_post




#게시글 목록조회, openapi문서 -예외처리 추가
@app.get(
    "/posts/",
    response_model=List[PostResponse],
    summary="게시글 목록 조회",
    description="게시글 목록을 조회합니다.",
    responses={
        404: {
            "description": "게시글 조회 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "게시글을 찾을 수 없습니다."
                    }
                }
            }
        }
    }
)
def get_posts( post_service:PostService = Depends(get_post_service)):
    post_in_db = post_service.get_posts()
    
    if post_in_db is None:
        raise HTTPException(status_code = 404, detail="게시글을 찾을 수 없습니다")
    
    return post_in_db



#게시글 상세 조회
@app.get("/post/{post_id}",response_model=PostResponse)
def get_post(post_id: int, post_service:PostService= Depends(get_post_service)):
    post_in_db = post_service.get_post(post_id)

    if post_in_db is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    
    return post_in_db



#게시글 수정
@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_update: PostUpdate, post_service: PostService=Depends(get_post_service)):
    post_in_db = post_service.update_post(post_id,post_update)

    if post_in_db is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return post_in_db



#게시글 삭제
@app.delete("/posts/{post_id}", response_model=dict)
def delete_post(post_id: int, post_service: PostService=Depends(get_post_service)):
    result = post_service.delete_post(post_id)

    if result is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return {"message": "게시글이 성공적으로 삭제되었습니다."}
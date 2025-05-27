from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse, PostUpdate


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
def create_post(post:PostCreate, db: Session = Depends(get_db)):
    new_post = Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

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
def get_posts(db: Session = Depends(get_db)):
    query = (
        select(Post).
        order_by(Post.created_at.desc)
    )
    posts = db.execute(query).scalars().all()

    #SQLAlchemy 2.0 이후 사용안하는 방식
    #posts = db.query(Post).order_by(Post.created_at.desc()).all()

    if posts is None:
        raise HTTPException(status_code = 404, detail="게시글을 찾을 수 없습니다")
    
    return posts

#게시글 상세 조회
@app.get("/post/{post_id}",response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    query = (
        select(Post).
        where(Post.id == post_id)
    )
    post = db.execute(query).scalar_one_or_none()

    #post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    return post



#게시글 수정
@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db)):
    query = (
        select(Post).
        where(Post.id == post_id)
    )
    post = db.execute(query).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    update_dict = {
        key: value
        for key, value in post_update.model_dump().items()
        if value is not None
    }

    for key, value in update_dict.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)

    return post



#게시글 삭제
@app.delete("/posts/{post_id}", response_model=dict)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    query = (
        select(Post).
        where(Post.id == post_id)
    )
    post = db.execute(query).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    db.delete(post)
    db.commit()

    return {"message": "게시글이 성공적으로 삭제되었습니다."}

from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse, PostUpdate



class PostService:
    def __init__(self, db: Session):
        self.db = db
    

    #게시글 생성
    def create_post(self, post_data: PostCreate):
        new_post = Post(**post_data.model_dump())
        self.db.add(new_post)
        self.db.commit()
        self.db.refresh(new_post)
        
        return new_post
    

    #게시글 조회
    def get_posts(self):
        query = (
            select(Post).
            order_by(Post.created_at.desc)
        )
        posts_in_db = self.db.execute(query).scalars().all()

        #SQLAlchemy 2.0 이후 사용안하는 방식
        #posts = db.query(Post).order_by(Post.created_at.desc()).all()
        
        return posts_in_db
    



    #게시글 상세조회
    def get_post(self, post_id: int):
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post_in_db = self.db.execute(query).scalar_one_or_none()

        #post = db.query(Post).filter(Post.id == post_id).first()

        return post_in_db
    




    #게시글 수정
    def update_post(self, post_id: int, update_post: PostUpdate):
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post_in_db = self.db.execute(query).scalar_one_or_none()

        if post_in_db is None:
            return None

        update_dict = {
            key: value
            for key, value in update_post.model_dump().items()
            if value is not None
        }
        '''
        update_post.model_dump() : 
                                    { "title"   : "새로운 제목",
                                      "content" : None         }
        '''
        
        # 게시글을 입력받은 내용으로 변경(setattr)
        for key, value in update_dict.items():
            setattr(post_in_db, key, value)

        self.db.commit()
        self.db.refresh(post_in_db)

        return post_in_db




    #게시글 삭제 -return 값 변경(boolean)
    def delete_post(self, post_id: int):
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post_in_db = self.db.execute(query).scalar_one_or_none()

        if post_in_db is None:
            return False
        
        self.db.delete(post_in_db)
        self.db.commit()

        return True


#팩토리함수
def get_post_service(db: Session= Depends(get_db)):
    return PostService(db)
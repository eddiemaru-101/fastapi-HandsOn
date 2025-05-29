from pydantic import BaseModel
from datetime import datetime
# DTO 설정


#게시글 생성 요청
class PostCreate(BaseModel):
    #입력받는 내용: 제목, 작성자, 내용
    title  : str
    author : str
    content: str

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

#응답
class PostResponse(BaseModel):
    #데이터 생성 확인을 위해 id, create 추가
    id        : int
    title     : str
    author    : str
    content   : str
    created_at: datetime

    class Config:
        #sqlalchemy -> pydantic 변환을 위한 설정
        from_attributes = True

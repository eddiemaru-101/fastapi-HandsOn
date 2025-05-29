from sqlalchemy import create_engine  # DB 연결을 생성하는 함수
from sqlalchemy.ext.declarative import declarative_base  # 모델 클래스의 베이스 클래스 생성용
from sqlalchemy.orm import sessionmaker  # 세션 객체를 만들어주는 팩토리 함수


# SQLite 데이터베이스 경로 설정. 상대경로 './sql_app.db'에 생성됨
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 데이터베이스 엔진 생성
# - SQLite 사용 시 다중 쓰레드 접근 이슈 때문에 connect_args 사용
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  
)

# 세션 클래스 생성
# - autocommit: 자동 커밋 비활성화 (명시적으로 커밋해야 반영됨)
# - autoflush: 자동 플러시 비활성화 (세션 커밋 전까지는 DB에 적용 안 됨)
# - bind: 어떤 DB에 연결할지 지정 (위의 engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 모델 클래스의 베이스 클래스 정의
# - 이 클래스를 상속받아 테이블 정의
Base = declarative_base()


# DB 세션 의존성 함수
# 제너레이터 yield 
def get_db():
    db = SessionLocal()
    try:
        yield db        
    finally:
        db.close()
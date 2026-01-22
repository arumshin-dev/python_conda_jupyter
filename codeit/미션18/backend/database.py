from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# sqlite 데이터베이스 연결
SQLALCHEMY_DATABASE_URL = "sqlite:///./movies.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 데이터베이스 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 모델 생성
Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# DB 연결
SQLALCHEMY_DATABASE_URL = "sqlite:///./movies.db"  # 예시: SQLite 사용
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Base 클래스 선언
Base = declarative_base()

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

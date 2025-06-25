import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash

# 테스트용 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 모델을 import하여 메타데이터에 등록
from app.models import User, Conversation, Message, LearningPath, AITool, Report, Content, ContentCategory


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """테스트용 데이터베이스 세션"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # 테스트용 초기 데이터 생성
    create_test_data(db)
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    """의존성 주입 오버라이드"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# FastAPI 앱의 의존성 오버라이드는 나중에 설정


def create_test_data(db: Session):
    """테스트용 초기 데이터 생성"""
    # 슈퍼 관리자 생성
    super_admin = User(
        email="admin@ai-tutor.com",
        password_hash=get_password_hash("admin123!@#"),
        name="슈퍼 관리자",
        role="super_admin",
        is_active=True
    )
    db.add(super_admin)
    
    # 기관 관리자 생성
    inst_admin = User(
        email="institution@ai-tutor.com",
        password_hash=get_password_hash("inst123!"),
        name="기관 관리자",
        role="institution_admin",
        institution_id="INST001",
        is_active=True
    )
    db.add(inst_admin)
    
    # 일반 사용자 생성
    user = User(
        email="user@ai-tutor.com",
        password_hash=get_password_hash("user123!"),
        name="일반 사용자",
        role="user",
        is_active=True
    )
    db.add(user)
    
    db.commit()


@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 fixture"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def client():
    """테스트용 HTTP 클라이언트"""
    from httpx import AsyncClient, ASGITransport
    
    # 테스트 데이터베이스 초기화
    Base.metadata.create_all(bind=engine)
    
    # 테스트 데이터 생성
    db = TestingSessionLocal()
    create_test_data(db)
    db.close()
    
    # DB 의존성 오버라이드
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # 정리
    Base.metadata.drop_all(bind=engine)
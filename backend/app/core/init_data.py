"""
초기 데이터 생성 스크립트
"""
from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.services.user_service import get_user_by_email


def create_super_admin(db: Session):
    """슈퍼 관리자 계정 생성"""
    super_admin_email = "admin@ai-tutor.com"
    
    # 이미 존재하는지 확인
    existing_admin = get_user_by_email(db, email=super_admin_email)
    if existing_admin:
        print(f"Super admin already exists: {super_admin_email}")
        return existing_admin
    
    # 슈퍼 관리자 생성
    super_admin = User(
        email=super_admin_email,
        password_hash=get_password_hash("admin123!@#"),
        name="시스템 관리자",
        role=UserRole.super_admin,
        is_active=True,
        job_title="System Administrator",
        department="IT"
    )
    
    db.add(super_admin)
    db.commit()
    db.refresh(super_admin)
    
    print(f"Super admin created: {super_admin_email}")
    print("Password: admin123!@#")
    return super_admin


def create_test_users(db: Session):
    """테스트 사용자 생성"""
    test_users = [
        {
            "email": "institution@ai-tutor.com",
            "password": "inst123!",
            "name": "기관 관리자",
            "role": UserRole.institution_admin,
            "institution_id": "INST001",
            "job_title": "Course Manager",
            "department": "Education"
        },
        {
            "email": "user@ai-tutor.com",
            "password": "user123!",
            "name": "일반 사용자",
            "role": UserRole.user,
            "job_title": "Developer",
            "department": "Engineering"
        }
    ]
    
    for user_data in test_users:
        existing_user = get_user_by_email(db, email=user_data["email"])
        if existing_user:
            print(f"User already exists: {user_data['email']}")
            continue
        
        password = user_data.pop("password")
        user = User(
            **user_data,
            password_hash=get_password_hash(password),
            is_active=True
        )
        
        db.add(user)
        print(f"User created: {user_data['email']} (Password: {password})")
    
    db.commit()


def init_data():
    """초기 데이터 생성"""
    db = next(get_db())
    try:
        create_super_admin(db)
        create_test_users(db)
    finally:
        db.close()


if __name__ == "__main__":
    init_data()
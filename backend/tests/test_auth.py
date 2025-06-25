import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import Session
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.main import app

class TestAuthentication:
    """인증 시스템 테스트"""
    
    @pytest.mark.asyncio
    async def test_user_registration(self, client):
        """TC-AUTH-001: 사용자 회원가입"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@test.com",
                "password": "Test123!@#",
                "name": "테스트 사용자",
                "job_title": "개발자",
                "department": "IT"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "user"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_user_login(self, client):
        """TC-AUTH-002: 사용자 로그인"""
        # 먼저 사용자 생성
        await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "logintest@test.com",
                "password": "Test123!@#",
                "name": "로그인 테스트"
            }
        )
        
        # 로그인 시도
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "logintest@test.com",
                "password": "Test123!@#"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_admin_access_control(self, client):
        """TC-AUTH-003: 관리자 권한 접근 제어"""
        # 일반 사용자로 로그인
        user_token = await self._get_user_token(client, "user")
        
        # 관리자 엔드포인트 접근 시도
        response = await client.get(
            "/api/v1/admin/stats",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
        
        # 관리자로 로그인
        admin_token = await self._get_admin_token(client)
        
        # 관리자 엔드포인트 접근
        response = await client.get(
            "/api/v1/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_three_tier_permissions(self, client):
        """TC-AUTH-004: 3단계 권한 시스템"""
        # 각 권한 레벨별 테스트
        roles = [
            ("user", False, False),
            ("institution_admin", True, False),
            ("super_admin", True, True)
        ]
        
        for role, can_access_admin, can_manage_all_users in roles:
            token = await self._get_token_for_role(client, role)
            
            # 관리자 대시보드 접근
            response = await client.get(
                "/api/v1/admin/stats",
                headers={"Authorization": f"Bearer {token}"}
            )
            if can_access_admin:
                assert response.status_code == 200
            else:
                assert response.status_code == 403
            
            # 전체 사용자 관리 (super_admin only)
            if can_access_admin:
                response = await client.get(
                    "/api/v1/admin/users",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if can_manage_all_users:
                    assert response.status_code == 200
                else:
                    # institution_admin은 자신의 기관 사용자만 볼 수 있음
                    assert response.status_code == 200
                    data = response.json()
                    # 실제로는 기관별 필터링이 적용되어야 함
    
    async def _get_user_token(self, client, role="user"):
        """테스트용 사용자 토큰 생성"""
        email = f"test_{role}@test.com"
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "password": "Test123!@#",
                "name": f"테스트 {role}"
            }
        )
        
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": email,
                "password": "Test123!@#"
            }
        )
        return response.json()["access_token"]
    
    async def _get_admin_token(self, client):
        """테스트용 관리자 토큰 생성"""
        # 실제 환경에서는 DB에 직접 관리자 생성
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "admin@ai-tutor.com",
                "password": "admin123!@#"
            }
        )
        return response.json()["access_token"]
    
    async def _get_token_for_role(self, client, role):
        """특정 권한의 토큰 생성"""
        if role == "super_admin":
            return await self._get_admin_token(client)
        else:
            return await self._get_user_token(client, role)
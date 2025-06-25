import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from datetime import datetime, timedelta

class TestReportGeneration:
    """리포트 생성 시스템 테스트"""
    
    @pytest.fixture
    async def admin_token(self):
        """관리자 토큰 fixture"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "admin@ai-tutor.com",
                    "password": "admin123!@#"
                }
            )
            return response.json()["access_token"]
    
    @pytest.mark.asyncio
    async def test_generate_user_progress_report(self, admin_token):
        """TC-REPORT-001: 사용자 진도 리포트 생성"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 리포트 생성 요청
            response = await client.post(
                "/api/v1/admin/reports/generate",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "report_type": "user_progress",
                    "format": "pdf",
                    "parameters": {
                        "date_from": (datetime.now() - timedelta(days=30)).isoformat(),
                        "date_to": datetime.now().isoformat(),
                        "user_ids": []
                    }
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["report_type"] == "user_progress"
            assert data["status"] == "pending"
            assert "id" in data
            return data["id"]
    
    @pytest.mark.asyncio
    async def test_report_progress_tracking(self, admin_token):
        """TC-REPORT-002: 리포트 생성 진행 상태 추적"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 리포트 생성
            report_id = await self.test_generate_user_progress_report(admin_token)
            
            # 진행 상태 확인
            max_attempts = 10
            for i in range(max_attempts):
                response = await client.get(
                    f"/api/v1/admin/reports/{report_id}/progress",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                assert response.status_code == 200
                data = response.json()
                
                assert "progress" in data
                assert "status" in data
                assert "message" in data
                
                if data["status"] in ["completed", "failed"]:
                    break
                
                await asyncio.sleep(2)  # 2초 대기
    
    @pytest.mark.asyncio
    async def test_generate_multiple_report_types(self, admin_token):
        """TC-REPORT-003: 다양한 리포트 유형 생성"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            report_types = [
                "user_progress",
                "learning_analytics",
                "ai_usage",
                "monthly_summary",
                "custom_report"
            ]
            
            report_ids = []
            for report_type in report_types:
                response = await client.post(
                    "/api/v1/admin/reports/generate",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json={
                        "report_type": report_type,
                        "format": "excel" if report_type == "learning_analytics" else "pdf",
                        "parameters": {
                            "date_from": (datetime.now() - timedelta(days=30)).isoformat(),
                            "date_to": datetime.now().isoformat()
                        }
                    }
                )
                assert response.status_code == 200
                report_ids.append(response.json()["id"])
            
            # 리포트 목록 확인
            response = await client.get(
                "/api/v1/admin/reports",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] >= len(report_ids)
    
    @pytest.mark.asyncio
    async def test_report_formats(self, admin_token):
        """TC-REPORT-004: 다양한 리포트 포맷 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            formats = ["pdf", "excel", "csv"]
            
            for format_type in formats:
                response = await client.post(
                    "/api/v1/admin/reports/generate",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json={
                        "report_type": "ai_usage",
                        "format": format_type,
                        "parameters": {}
                    }
                )
                assert response.status_code == 200
                data = response.json()
                assert data["format"] == format_type
    
    @pytest.mark.asyncio
    async def test_report_filtering(self, admin_token):
        """TC-REPORT-005: 리포트 목록 필터링"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 특정 타입의 리포트 조회
            response = await client.get(
                "/api/v1/admin/reports",
                headers={"Authorization": f"Bearer {admin_token}"},
                params={"report_type": "user_progress"}
            )
            assert response.status_code == 200
            data = response.json()
            
            # 모든 리포트가 user_progress 타입인지 확인
            if data["total"] > 0:
                assert all(r["report_type"] == "user_progress" for r in data["reports"])
    
    @pytest.mark.asyncio
    async def test_report_access_control(self, admin_token):
        """TC-REPORT-006: 리포트 접근 권한 제어"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 관리자로 리포트 생성
            response = await client.post(
                "/api/v1/admin/reports/generate",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "report_type": "monthly_summary",
                    "format": "pdf",
                    "parameters": {}
                }
            )
            report_id = response.json()["id"]
            
            # 일반 사용자 토큰으로 접근 시도
            user_response = await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "normaluser@test.com",
                    "password": "Test123!@#",
                    "name": "일반 사용자"
                }
            )
            
            login_response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "normaluser@test.com",
                    "password": "Test123!@#"
                }
            )
            user_token = login_response.json()["access_token"]
            
            # 일반 사용자는 리포트에 접근할 수 없어야 함
            response = await client.get(
                f"/api/v1/admin/reports/{report_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403
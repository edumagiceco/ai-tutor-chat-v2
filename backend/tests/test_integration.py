import pytest
from httpx import AsyncClient
from app.main import app
import asyncio

class TestIntegrationScenarios:
    """통합 시나리오 테스트"""
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self):
        """TC-INT-001: 전체 사용자 여정 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. 회원가입
            response = await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "journey@test.com",
                    "password": "Test123!@#",
                    "name": "여정 테스트",
                    "job_title": "개발자",
                    "department": "IT"
                }
            )
            assert response.status_code == 200
            user_id = response.json()["id"]
            
            # 2. 로그인
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "journey@test.com",
                    "password": "Test123!@#"
                }
            )
            assert response.status_code == 200
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3. 학습 경로 조회
            response = await client.get(
                "/api/v1/learning/path",
                headers=headers
            )
            assert response.status_code == 200
            
            # 4. 대화 시작
            response = await client.post(
                "/api/v1/chat/conversations",
                headers=headers,
                json={"title": "첫 대화"}
            )
            assert response.status_code == 200
            conversation_id = response.json()["id"]
            
            # 5. 메시지 전송
            response = await client.post(
                f"/api/v1/chat/conversations/{conversation_id}/messages",
                headers=headers,
                json={"content": "ChatGPT 사용법을 알려주세요"}
            )
            assert response.status_code == 200
            
            # 6. AI 도구 조회
            response = await client.get(
                "/api/v1/learning/ai-tools",
                headers=headers
            )
            assert response.status_code == 200
            
            # 7. 학습 진도 업데이트
            response = await client.put(
                "/api/v1/learning/progress",
                headers=headers,
                json={"progress": 25}
            )
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_admin_workflow(self):
        """TC-INT-002: 관리자 워크플로우 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. 관리자 로그인
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "admin@ai-tutor.com",
                    "password": "admin123!@#"
                }
            )
            assert response.status_code == 200
            admin_token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # 2. 대시보드 통계 조회
            response = await client.get(
                "/api/v1/admin/stats",
                headers=headers
            )
            assert response.status_code == 200
            stats = response.json()
            assert "total_users" in stats
            
            # 3. 콘텐츠 생성
            response = await client.post(
                "/api/v1/admin/contents",
                headers=headers,
                json={
                    "title": "신규 학습 자료",
                    "slug": "new-learning-material",
                    "content": "# 새로운 학습 자료\n\n내용...",
                    "content_type": "tutorial"
                }
            )
            assert response.status_code == 200
            content_id = response.json()["id"]
            
            # 4. RAG 문서 업로드
            response = await client.post(
                "/api/v1/admin/rag/documents/upload-text",
                headers=headers,
                json={
                    "title": "관리자 가이드",
                    "content": "관리자 기능 사용 가이드..."
                }
            )
            assert response.status_code == 200
            
            # 5. 리포트 생성
            response = await client.post(
                "/api/v1/admin/reports/generate",
                headers=headers,
                json={
                    "report_type": "monthly_summary",
                    "format": "pdf",
                    "parameters": {}
                }
            )
            assert response.status_code == 200
            report_id = response.json()["id"]
            
            # 6. 사용자 관리
            response = await client.get(
                "/api/v1/admin/users",
                headers=headers,
                params={"limit": 10}
            )
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """TC-INT-003: 동시성 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 여러 사용자 동시 생성
            async def create_user(index):
                response = await client.post(
                    "/api/v1/auth/signup",
                    json={
                        "email": f"concurrent{index}@test.com",
                        "password": "Test123!@#",
                        "name": f"동시 사용자 {index}"
                    }
                )
                return response.status_code == 200
            
            # 10명의 사용자 동시 생성
            tasks = [create_user(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            assert all(results)
            
            # 동시 로그인
            async def login_user(index):
                response = await client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": f"concurrent{index}@test.com",
                        "password": "Test123!@#"
                    }
                )
                return response.json()["access_token"]
            
            tokens = await asyncio.gather(*[login_user(i) for i in range(10)])
            assert all(tokens)
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """TC-INT-004: 에러 복구 시나리오"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. 잘못된 로그인 시도
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "nonexistent@test.com",
                    "password": "wrongpassword"
                }
            )
            assert response.status_code == 401
            
            # 2. 잘못된 토큰으로 API 호출
            response = await client.get(
                "/api/v1/learning/path",
                headers={"Authorization": "Bearer invalid_token"}
            )
            assert response.status_code == 401
            
            # 3. 존재하지 않는 리소스 접근
            response = await client.get(
                "/api/v1/chat/conversations/99999",
                headers={"Authorization": "Bearer some_token"}
            )
            assert response.status_code in [401, 404]
            
            # 4. 잘못된 데이터 형식
            response = await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "invalid-email",  # 잘못된 이메일 형식
                    "password": "123",  # 너무 짧은 비밀번호
                    "name": ""  # 빈 이름
                }
            )
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_data_consistency(self):
        """TC-INT-005: 데이터 일관성 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 관리자 로그인
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "admin@ai-tutor.com",
                    "password": "admin123!@#"
                }
            )
            admin_token = response.json()["access_token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            
            # 1. 사용자 생성
            response = await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "consistency@test.com",
                    "password": "Test123!@#",
                    "name": "일관성 테스트"
                }
            )
            user_id = response.json()["id"]
            
            # 2. 사용자 로그인
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "consistency@test.com",
                    "password": "Test123!@#"
                }
            )
            user_token = response.json()["access_token"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
            
            # 3. 사용자가 대화 생성
            response = await client.post(
                "/api/v1/chat/conversations",
                headers=user_headers,
                json={"title": "테스트 대화"}
            )
            conversation_id = response.json()["id"]
            
            # 4. 관리자가 통계에서 확인
            response = await client.get(
                "/api/v1/admin/stats",
                headers=admin_headers
            )
            stats = response.json()
            initial_conversations = stats["total_conversations"]
            
            # 5. 더 많은 대화 생성
            for i in range(3):
                await client.post(
                    "/api/v1/chat/conversations",
                    headers=user_headers,
                    json={"title": f"대화 {i}"}
                )
            
            # 6. 통계 재확인
            response = await client.get(
                "/api/v1/admin/stats",
                headers=admin_headers
            )
            stats = response.json()
            assert stats["total_conversations"] >= initial_conversations + 3
import pytest
from httpx import AsyncClient
from app.main import app

class TestContentManagement:
    """콘텐츠 관리 시스템 테스트"""
    
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
    async def test_create_content_category(self, admin_token):
        """TC-CONTENT-001: 콘텐츠 카테고리 생성"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/admin/content-categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "name": "AI 기초",
                    "slug": "ai-basics",
                    "description": "AI 기초 학습 자료"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "AI 기초"
            assert data["slug"] == "ai-basics"
            return data["id"]
    
    @pytest.mark.asyncio
    async def test_create_content(self, admin_token):
        """TC-CONTENT-002: 콘텐츠 생성"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 먼저 카테고리 생성
            category_id = await self.test_create_content_category(admin_token)
            
            # 콘텐츠 생성
            response = await client.post(
                "/api/v1/admin/contents",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "title": "ChatGPT 시작하기",
                    "slug": "getting-started-chatgpt",
                    "content": "# ChatGPT 시작하기\n\nChatGPT는...",
                    "content_type": "tutorial",
                    "category_id": category_id,
                    "tags": ["chatgpt", "ai", "tutorial"],
                    "meta_description": "ChatGPT 사용법을 배워보세요"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "ChatGPT 시작하기"
            assert data["status"] == "draft"
            assert data["content_type"] == "tutorial"
            return data["id"]
    
    @pytest.mark.asyncio
    async def test_publish_content(self, admin_token):
        """TC-CONTENT-003: 콘텐츠 발행"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 콘텐츠 생성
            content_id = await self.test_create_content(admin_token)
            
            # 발행
            response = await client.post(
                f"/api/v1/admin/contents/{content_id}/publish",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "published"
            assert data["published_at"] is not None
    
    @pytest.mark.asyncio
    async def test_content_versioning(self, admin_token):
        """TC-CONTENT-004: 콘텐츠 버전 관리"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 콘텐츠 생성
            content_id = await self.test_create_content(admin_token)
            
            # 콘텐츠 업데이트 (새 버전 생성)
            response = await client.put(
                f"/api/v1/admin/contents/{content_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "content": "# ChatGPT 시작하기 (수정됨)\n\n업데이트된 내용..."
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["version"] == 2
    
    @pytest.mark.asyncio
    async def test_content_search_filter(self, admin_token):
        """TC-CONTENT-005: 콘텐츠 검색 및 필터링"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 여러 콘텐츠 생성
            for i in range(3):
                await client.post(
                    "/api/v1/admin/contents",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json={
                        "title": f"테스트 콘텐츠 {i}",
                        "slug": f"test-content-{i}",
                        "content": f"내용 {i}",
                        "content_type": "article" if i % 2 == 0 else "tutorial"
                    }
                )
            
            # 검색
            response = await client.get(
                "/api/v1/admin/contents",
                headers={"Authorization": f"Bearer {admin_token}"},
                params={"search": "테스트"}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) >= 3
            
            # 필터링
            response = await client.get(
                "/api/v1/admin/contents",
                headers={"Authorization": f"Bearer {admin_token}"},
                params={"content_type": "article"}
            )
            assert response.status_code == 200
            data = response.json()
            assert all(item["content_type"] == "article" for item in data)
    
    @pytest.mark.asyncio
    async def test_hierarchical_categories(self, admin_token):
        """TC-CONTENT-006: 계층적 카테고리 구조"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 부모 카테고리 생성
            response = await client.post(
                "/api/v1/admin/content-categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "name": "프로그래밍",
                    "slug": "programming"
                }
            )
            parent_id = response.json()["id"]
            
            # 자식 카테고리 생성
            response = await client.post(
                "/api/v1/admin/content-categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "name": "Python",
                    "slug": "python",
                    "parent_id": parent_id
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["parent_id"] == parent_id
            
            # 카테고리 트리 조회
            response = await client.get(
                "/api/v1/admin/content-categories",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            categories = response.json()
            
            # 부모 카테고리 찾기
            parent = next(c for c in categories if c["id"] == parent_id)
            assert len(parent.get("children", [])) > 0
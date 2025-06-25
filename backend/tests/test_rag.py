import pytest
from httpx import AsyncClient
from app.main import app
import os
import tempfile

class TestRAGDocumentManagement:
    """RAG 문서 관리 시스템 테스트"""
    
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
    async def test_document_upload_text(self, admin_token):
        """TC-RAG-001: 텍스트 문서 업로드"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/admin/rag/documents/upload-text",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "title": "AI 학습 가이드",
                    "content": "인공지능(AI)은 인간의 지능을 모방하는 컴퓨터 시스템입니다.",
                    "metadata": {
                        "category": "기초",
                        "author": "관리자"
                    }
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "AI 학습 가이드"
            assert data["doc_type"] == "text"
            assert "id" in data
            return data["id"]
    
    @pytest.mark.asyncio
    async def test_document_upload_file(self, admin_token):
        """TC-RAG-002: 파일 문서 업로드"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("이것은 테스트 문서입니다.\nRAG 시스템 테스트를 위한 내용입니다.")
                temp_file = f.name
            
            try:
                with open(temp_file, 'rb') as f:
                    response = await client.post(
                        "/api/v1/admin/rag/documents/upload",
                        headers={"Authorization": f"Bearer {admin_token}"},
                        files={"file": ("test.txt", f, "text/plain")},
                        data={"metadata": '{"category": "test"}'}
                    )
                assert response.status_code == 200
                data = response.json()
                assert data["filename"] == "test.txt"
                assert data["doc_type"] == "file"
            finally:
                os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_document_embedding_generation(self, admin_token):
        """TC-RAG-003: 문서 임베딩 생성 확인"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 문서 업로드
            doc_id = await self.test_document_upload_text(admin_token)
            
            # 문서 상세 조회
            response = await client.get(
                f"/api/v1/admin/rag/documents/{doc_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            
            # 임베딩이 생성되었는지 확인
            assert data["chunk_count"] > 0
            assert data["status"] == "processed"
    
    @pytest.mark.asyncio
    async def test_document_search(self, admin_token):
        """TC-RAG-004: 문서 검색 기능"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 여러 문서 업로드
            docs = [
                {"title": "Python 프로그래밍", "content": "Python은 배우기 쉬운 프로그래밍 언어입니다."},
                {"title": "JavaScript 기초", "content": "JavaScript는 웹 개발의 핵심 언어입니다."},
                {"title": "AI와 머신러닝", "content": "머신러닝은 AI의 한 분야입니다."}
            ]
            
            for doc in docs:
                await client.post(
                    "/api/v1/admin/rag/documents/upload-text",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json=doc
                )
            
            # 검색
            response = await client.get(
                "/api/v1/admin/rag/documents",
                headers={"Authorization": f"Bearer {admin_token}"},
                params={"search": "프로그래밍"}
            )
            assert response.status_code == 200
            data = response.json()
            
            # 검색 결과 확인
            assert len(data) >= 1
            assert any("프로그래밍" in doc["title"] or "프로그래밍" in doc.get("content", "") 
                      for doc in data)
    
    @pytest.mark.asyncio
    async def test_document_metadata_filtering(self, admin_token):
        """TC-RAG-005: 메타데이터 기반 필터링"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 다양한 카테고리의 문서 업로드
            categories = ["기초", "중급", "고급"]
            for cat in categories:
                await client.post(
                    "/api/v1/admin/rag/documents/upload-text",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json={
                        "title": f"{cat} 레벨 문서",
                        "content": f"이것은 {cat} 레벨의 학습 자료입니다.",
                        "metadata": {"category": cat}
                    }
                )
            
            # 특정 카테고리 필터링
            response = await client.get(
                "/api/v1/admin/rag/documents",
                headers={"Authorization": f"Bearer {admin_token}"},
                params={"metadata": '{"category": "기초"}'}
            )
            assert response.status_code == 200
            data = response.json()
            
            # 모든 문서가 기초 카테고리인지 확인
            for doc in data:
                if "metadata" in doc and doc["metadata"]:
                    assert doc["metadata"].get("category") == "기초"
    
    @pytest.mark.asyncio
    async def test_document_deletion(self, admin_token):
        """TC-RAG-006: 문서 삭제"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 문서 업로드
            doc_id = await self.test_document_upload_text(admin_token)
            
            # 문서 삭제
            response = await client.delete(
                f"/api/v1/admin/rag/documents/{doc_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            
            # 삭제된 문서 조회 시도
            response = await client.get(
                f"/api/v1/admin/rag/documents/{doc_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_rag_context_retrieval(self, admin_token):
        """TC-RAG-007: RAG 컨텍스트 검색"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 관련 문서들 업로드
            docs = [
                {
                    "title": "ChatGPT 활용법",
                    "content": "ChatGPT는 대화형 AI로, 질문에 답하고 작업을 도와줍니다."
                },
                {
                    "title": "프롬프트 엔지니어링",
                    "content": "좋은 프롬프트는 명확하고 구체적이어야 합니다."
                }
            ]
            
            for doc in docs:
                await client.post(
                    "/api/v1/admin/rag/documents/upload-text",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json=doc
                )
            
            # 유사 문서 검색
            response = await client.post(
                "/api/v1/rag/search",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "query": "ChatGPT 사용 방법",
                    "top_k": 3
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) > 0
            assert data["results"][0]["score"] > 0.5  # 유사도 점수 확인
    
    @pytest.mark.asyncio
    async def test_document_chunking(self, admin_token):
        """TC-RAG-008: 대용량 문서 청킹"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 긴 문서 생성
            long_content = "\n\n".join([
                f"섹션 {i}: 이것은 매우 긴 문서의 {i}번째 섹션입니다. " * 10
                for i in range(10)
            ])
            
            response = await client.post(
                "/api/v1/admin/rag/documents/upload-text",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "title": "대용량 문서",
                    "content": long_content
                }
            )
            assert response.status_code == 200
            doc_id = response.json()["id"]
            
            # 문서 상세 조회로 청크 수 확인
            response = await client.get(
                f"/api/v1/admin/rag/documents/{doc_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            
            # 여러 청크로 나뉘었는지 확인
            assert data["chunk_count"] > 1
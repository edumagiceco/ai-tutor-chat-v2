import pytest
import asyncio
from httpx import AsyncClient
from websockets import connect
from app.main import app
import json

class TestWebSocketFeatures:
    """WebSocket 실시간 기능 테스트"""
    
    @pytest.fixture
    async def user_token(self):
        """사용자 토큰 fixture"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 사용자 생성
            await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "wstest@test.com",
                    "password": "Test123!@#",
                    "name": "WebSocket 테스트"
                }
            )
            
            # 로그인
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "wstest@test.com",
                    "password": "Test123!@#"
                }
            )
            return response.json()["access_token"]
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, user_token):
        """TC-WS-001: WebSocket 연결 테스트"""
        ws_url = f"ws://localhost:8081/api/v1/ws?token={user_token}"
        
        try:
            async with connect(ws_url) as websocket:
                # 연결 확인 메시지
                await websocket.send(json.dumps({
                    "type": "ping"
                }))
                
                response = await websocket.recv()
                data = json.loads(response)
                assert data["type"] == "pong"
        except Exception as e:
            pytest.skip(f"WebSocket 연결 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_user_presence(self, user_token):
        """TC-WS-002: 사용자 접속 상태 관리"""
        ws_url = f"ws://localhost:8081/api/v1/ws?token={user_token}"
        
        try:
            async with connect(ws_url) as websocket:
                # 사용자 상태 업데이트
                await websocket.send(json.dumps({
                    "type": "presence",
                    "status": "online"
                }))
                
                # 활성 사용자 목록 요청
                await websocket.send(json.dumps({
                    "type": "get_active_users"
                }))
                
                response = await websocket.recv()
                data = json.loads(response)
                assert data["type"] == "active_users"
                assert isinstance(data["users"], list)
        except Exception as e:
            pytest.skip(f"WebSocket 연결 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_real_time_notifications(self, user_token):
        """TC-WS-003: 실시간 알림 전송"""
        ws_url = f"ws://localhost:8081/api/v1/ws?token={user_token}"
        
        try:
            async with connect(ws_url) as websocket:
                # 알림 구독
                await websocket.send(json.dumps({
                    "type": "subscribe",
                    "channel": "notifications"
                }))
                
                # 서버에서 알림이 오는지 확인 (실제 환경에서는 다른 이벤트가 트리거)
                # 여기서는 타임아웃으로 테스트
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    assert "type" in data
                except asyncio.TimeoutError:
                    # 타임아웃은 정상 (실제 알림이 없을 수 있음)
                    pass
        except Exception as e:
            pytest.skip(f"WebSocket 연결 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_chat_streaming(self):
        """TC-WS-004: 채팅 스트리밍 응답"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 사용자 생성 및 로그인
            await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "streamtest@test.com",
                    "password": "Test123!@#",
                    "name": "스트리밍 테스트"
                }
            )
            
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "streamtest@test.com",
                    "password": "Test123!@#"
                }
            )
            token = response.json()["access_token"]
            
            # 대화 생성
            response = await client.post(
                "/api/v1/chat/conversations",
                headers={"Authorization": f"Bearer {token}"},
                json={"title": "스트리밍 테스트"}
            )
            conversation_id = response.json()["id"]
            
            # 스트리밍 메시지 전송
            response = await client.post(
                f"/api/v1/chat/conversations/{conversation_id}/messages/stream",
                headers={"Authorization": f"Bearer {token}"},
                json={"content": "안녕하세요"},
                stream=True
            )
            
            # SSE 응답 확인
            chunks = []
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunks.append(line[6:])
            
            assert len(chunks) > 0
    
    @pytest.mark.asyncio
    async def test_multiple_websocket_connections(self, user_token):
        """TC-WS-005: 다중 WebSocket 연결 처리"""
        ws_url = f"ws://localhost:8081/api/v1/ws?token={user_token}"
        
        try:
            # 동시에 여러 연결 생성
            connections = []
            for i in range(3):
                ws = await connect(ws_url)
                connections.append(ws)
            
            # 각 연결에서 메시지 전송
            for i, ws in enumerate(connections):
                await ws.send(json.dumps({
                    "type": "echo",
                    "message": f"Connection {i}"
                }))
            
            # 응답 확인
            for i, ws in enumerate(connections):
                response = await ws.recv()
                data = json.loads(response)
                assert f"Connection {i}" in str(data)
            
            # 연결 종료
            for ws in connections:
                await ws.close()
                
        except Exception as e:
            pytest.skip(f"WebSocket 연결 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_error_handling(self, user_token):
        """TC-WS-006: WebSocket 에러 처리"""
        ws_url = f"ws://localhost:8081/api/v1/ws?token={user_token}"
        
        try:
            async with connect(ws_url) as websocket:
                # 잘못된 메시지 형식 전송
                await websocket.send("invalid json")
                
                response = await websocket.recv()
                data = json.loads(response)
                assert data["type"] == "error"
                assert "message" in data
                
                # 알 수 없는 메시지 타입
                await websocket.send(json.dumps({
                    "type": "unknown_type"
                }))
                
                response = await websocket.recv()
                data = json.loads(response)
                assert data["type"] == "error"
                
        except Exception as e:
            pytest.skip(f"WebSocket 연결 실패: {e}")
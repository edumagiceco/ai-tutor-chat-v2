# AI 교육 챗봇 시스템 설계서 v2

## 시스템 구현 상태

### 완료된 작업
1. 전체 아키텍처 설계 완료
2. Docker Compose 기반 인프라 구성
3. 사용자 시스템 상세 기획 완료
4. 관리자 시스템 상세 기획 완료
5. 사용자 챗봇 시스템 구현 완료
   - FastAPI 백엔드 서버 구축
   - React TypeScript 프론트엔드 구현
   - AI 서비스 마이크로서비스 구축
   - MySQL 데이터베이스 스키마 구성
   - Redis 캐싱 시스템 설정
   - Qdrant 벡터 데이터베이스 연동
6. Docker 환경 실행 및 검증 완료
   - 모든 서비스 정상 작동 확인
   - 환경 변수 설정 완료
   - 네트워크 연결 검증

### 현재 진행 상태
- 날짜: 2025년 6월 24일
- 버전: v2.0
- 상태: Docker 환경에서 모든 서비스 정상 작동 중

### 접속 정보
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8081
- **API Documentation**: http://localhost:8081/docs
- **AI Service**: http://localhost:8000
- **MySQL**: localhost:3306
- **Redis**: localhost:6379
- **Qdrant**: localhost:6333

## 1. 시스템 아키텍처 개요

### 1.1 전체 구조
- **마이크로서비스 아키텍처** 기반
- **Docker Compose**를 통한 컨테이너 오케스트레이션
- **API Gateway** 패턴으로 통합된 엔드포인트 제공

### 1.2 주요 컴포넌트
1. **Frontend Service** (React.js)
2. **Backend API Service** (Python FastAPI)
3. **AI Service** (Python FastAPI - 별도 서비스)
4. **Database Service** (MySQL 8.0)
5. **Vector Database** (Qdrant)
6. **Cache Service** (Redis)
7. **Queue Service** (RabbitMQ)

## 2. 백엔드 아키텍처

### 2.1 Main API Server (Python FastAPI)
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── users.py
│   │   │   ├── courses.py
│   │   │   └── learning.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── learning_path.py
│   │   └── ai_tool.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── chat.py
│   │   └── learning.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── ai_service.py
│   │   └── vector_service.py
│   ├── middleware/
│   │   ├── rate_limiter.py
│   │   └── auth_middleware.py
│   └── main.py
├── requirements.txt
├── .env.example
└── Dockerfile
```

### 2.2 AI Service (Python FastAPI - 별도 서비스)
```
ai-service/
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   ├── embeddings.py
│   │   └── analytics.py
│   ├── core/
│   │   ├── claude_client.py
│   │   ├── rag_engine.py
│   │   └── vector_store.py
│   ├── models/
│   │   └── schemas.py
│   └── main.py
├── requirements.txt
└── Dockerfile
```

## 3. 프론트엔드 아키텍처

### 3.1 디렉토리 구조
```
frontend/
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── MessageList.jsx
│   │   │   └── InputArea.jsx
│   │   ├── Dashboard/
│   │   │   ├── LearningProgress.jsx
│   │   │   └── SkillMatrix.jsx
│   │   └── Common/
│   │       ├── Header.jsx
│   │       └── Sidebar.jsx
│   ├── pages/
│   │   ├── HomePage.jsx
│   │   ├── ChatPage.jsx
│   │   ├── LearningPathPage.jsx
│   │   └── ProfilePage.jsx
│   ├── contexts/
│   │   ├── AuthContext.jsx
│   │   └── ChatContext.jsx
│   ├── services/
│   │   └── api.js
│   └── App.js
├── package.json
└── Dockerfile
```

## 4. 데이터베이스 설계

### 4.1 MySQL 주요 테이블

```sql
-- 사용자 정보
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    job_title VARCHAR(100),
    department VARCHAR(100),
    ai_level ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'beginner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 대화 세션
CREATE TABLE conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 메시지 기록
CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id INT NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- 학습 경로
CREATE TABLE learning_paths (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    job_category VARCHAR(100) NOT NULL,
    current_level INT DEFAULT 1,
    progress DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- AI 도구 카탈로그
CREATE TABLE ai_tools (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty ENUM('basic', 'intermediate', 'advanced') NOT NULL,
    description TEXT,
    usage_guide TEXT
);
```

### 4.2 Qdrant 벡터 데이터베이스 구조

```python
# 컬렉션 구조
collections = {
    "educational_content": {
        "size": 1536,  # OpenAI embedding dimension
        "distance": "Cosine"
    },
    "user_interactions": {
        "size": 1536,
        "distance": "Cosine"
    },
    "ai_tools_embeddings": {
        "size": 1536,
        "distance": "Cosine"
    }
}

# 벡터 포인트 구조
point_structure = {
    "id": "uuid",
    "vector": [0.1, 0.2, ...],  # 1536 dimensions
    "payload": {
        "content": "text",
        "category": "string",
        "metadata": {}
    }
}
```

## 5. API 엔드포인트 설계

### 5.1 인증 API
- POST /api/v1/auth/signup
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- POST /api/v1/auth/refresh
- GET /api/v1/auth/me

### 5.2 채팅 API
- POST /api/v1/chat/conversations
- POST /api/v1/chat/conversations/{conversation_id}/messages
- GET /api/v1/chat/conversations
- GET /api/v1/chat/conversations/{conversation_id}
- DELETE /api/v1/chat/conversations/{conversation_id}

### 5.3 학습 관리 API
- GET /api/v1/learning/path
- POST /api/v1/learning/path
- PUT /api/v1/learning/progress
- GET /api/v1/learning/recommendations
- GET /api/v1/learning/achievements
- GET /api/v1/learning/ai-tools

### 5.4 RAG 및 벡터 검색 API
- POST /api/v1/search/similar
- POST /api/v1/embeddings/create
- GET /api/v1/search/tools

## 6. Docker Compose 구성

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8080
    depends_on:
      - backend
    networks:
      - ai-tutor-network

  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=mysql://magic7:ZAvEjgkEzu8K**@mysql:3306/magic7
      - REDIS_URL=redis://redis:6379
      - AI_SERVICE_URL=http://ai-service:8000
      - QDRANT_URL=http://qdrant:6333
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - mysql
      - redis
      - qdrant
      - ai-service
    networks:
      - ai-tutor-network

  ai-service:
    build: ./ai-service
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=mysql://magic7:ZAvEjgkEzu8K**@mysql:3306/magic7
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - mysql
      - qdrant
    networks:
      - ai-tutor-network

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=magic7
      - MYSQL_USER=magic7
      - MYSQL_PASSWORD=ZAvEjgkEzu8K**
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    networks:
      - ai-tutor-network

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - ai-tutor-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ai-tutor-network

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=admin
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - ai-tutor-network

volumes:
  mysql_data:
  qdrant_data:
  redis_data:
  rabbitmq_data:

networks:
  ai-tutor-network:
    driver: bridge
```

## 7. 환경 변수 설정 (.env)

```env
# API Keys
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Database
MYSQL_ROOT_PASSWORD=root_password
DB_HOST=mysql
DB_PORT=3306
DB_NAME=magic7
DB_USER=magic7
DB_PASSWORD=ZAvEjgkEzu8K**

# JWT
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRE_MINUTES=30

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# RabbitMQ
RABBITMQ_PASSWORD=rabbit_password

# Application
DEBUG=False
LOG_LEVEL=INFO
```

## 8. 주요 기술 스택 상세

### 8.1 백엔드 (FastAPI)
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **SQLAlchemy**: ORM (MySQL 연동)
- **Alembic**: 데이터베이스 마이그레이션
- **Pydantic**: 데이터 검증 및 스키마
- **python-jose**: JWT 토큰 처리
- **passlib**: 패스워드 해싱
- **celery**: 비동기 작업 처리
- **httpx**: 비동기 HTTP 클라이언트

### 8.2 AI/ML 스택
- **Anthropic Claude API**: 메인 대화 엔진
- **OpenAI API**: 임베딩 생성 (text-embedding-3-small)
- **Qdrant**: 벡터 검색 및 유사도 매칭
- **LangChain**: LLM 오케스트레이션
- **NumPy/Pandas**: 데이터 처리

### 8.3 프론트엔드
- **React.js 18**: UI 프레임워크
- **TypeScript**: 타입 안정성
- **Tailwind CSS**: 스타일링
- **Ant Design**: UI 컴포넌트
- **Socket.io-client**: 실시간 통신
- **Redux Toolkit**: 상태 관리
- **React Query**: 서버 상태 관리

## 9. 개발 단계별 구현 계획

### Phase 1: 기반 인프라 구축 (2주)
- [ ] Docker Compose 환경 설정
- [ ] MySQL 데이터베이스 스키마 생성
- [ ] Qdrant 벡터 DB 초기 설정
- [ ] FastAPI 기본 프로젝트 구조 생성
- [ ] React 프로젝트 초기화

### Phase 2: 핵심 백엔드 개발 (3주)
- [ ] 사용자 인증 시스템 구현
- [ ] 채팅 API 엔드포인트 개발
- [ ] AI 서비스 통합 (Claude API)
- [ ] RAG 시스템 구현
- [ ] 벡터 검색 기능 구현

### Phase 3: 프론트엔드 개발 (3주)
- [ ] 로그인/회원가입 UI
- [ ] 채팅 인터페이스 구현
- [ ] 대시보드 및 학습 진도 표시
- [ ] 실시간 통신 구현
- [ ] 반응형 디자인 적용

### Phase 4: 통합 및 최적화 (2주)
- [ ] 전체 시스템 통합 테스트
- [ ] 성능 최적화
- [ ] 보안 강화
- [ ] 배포 준비
- [ ] 문서화

## 10. 보안 및 성능 고려사항

### 10.1 보안
- JWT 기반 인증
- API 키 환경 변수 관리
- CORS 설정
- Rate Limiting
- SQL Injection 방지 (SQLAlchemy ORM)
- 입력 검증 (Pydantic)

### 10.2 성능
- Redis 캐싱 전략
- 비동기 처리 (FastAPI async/await)
- 데이터베이스 인덱싱
- 벡터 검색 최적화
- CDN 활용 (프론트엔드 자산)

## 11. 모니터링 및 로깅

- **Prometheus**: 메트릭 수집
- **Grafana**: 시각화 대시보드
- **ELK Stack**: 로그 관리
- **Sentry**: 에러 트래킹

## 12. 시스템 상세 기획 문서

### 12.1 사용자 챗봇 시스템
- **문서 위치**: `docs/user_system_plan.md`
- **주요 기능**: AI 대화 인터페이스, 학습 경로 관리, 실습 시스템, 성과 분석
- **기술 스택**: React.js + TypeScript + Tailwind CSS

### 12.2 관리자 시스템  
- **문서 위치**: `docs/admin_system_plan.md`
- **주요 기능**: 대시보드, 사용자 관리, 콘텐츠 관리, RAG 데이터 관리, 모니터링
- **권한 관리**: RBAC 기반 4단계 권한 체계

### 12.3 시스템 변경 사항
- **백엔드**: Node.js/Express → Python FastAPI
- **데이터베이스**: PostgreSQL → MySQL 8.0
- **벡터 DB**: Qdrant 추가 (RAG 및 임베딩 저장용)
- **상세 설계**: `docs/project_plan_v2.md` 참조

## 13. 개발 진행 상황

- [x] 시스템 요구사항 분석 완료
- [x] 전체 아키텍처 설계 완료
- [x] 사용자 시스템 상세 기획 완료
- [x] 관리자 시스템 상세 기획 완료
- [x] Docker 환경 구성 완료
- [x] Backend API 서버 개발 완료
  - FastAPI 프레임워크 설정
  - 인증 시스템 구현 (JWT)
  - 채팅 API 구현
  - 사용자 관리 API 구현
  - 학습 관리 API 구현
  - MySQL 데이터베이스 스키마 및 초기 데이터 설정
- [x] Frontend 애플리케이션 개발 완료
  - React + TypeScript 프로젝트 설정
  - Tailwind CSS 스타일링
  - 인증 시스템 UI (로그인/회원가입)
  - 채팅 인터페이스 구현
  - 학습 관리 페이지 구현
  - 사용자 프로필 페이지 구현
  - API 통신 서비스 구현
- [x] AI 서비스 통합 (기본 구조 완료)
  - Anthropic Claude API 연동
- [ ] 테스트 및 배포

**최종 업데이트**: 2025-06-24
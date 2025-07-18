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
- 날짜: 2025년 6월 25일
- 버전: v2.6
- 상태: Phase 3 프론트엔드 개발 완료, Phase 4 통합 및 최적화 진행 중
- 완료: 3단계 권한 시스템 구현, 관리자 UI 기본 구조, RAG 문서 관리 인터페이스, 통계 분석 페이지, 시스템 설정 페이지, 콘텐츠 관리 시스템, 리포트 생성 시스템

### 접속 정보
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8081
- **API Documentation**: http://localhost:8081/docs
- **AI Service**: http://localhost:8000
- **MySQL**: localhost:3306
- **Redis**: localhost:6379
- **Qdrant**: localhost:6333

### 초기 계정 정보
- **슈퍼 관리자**: admin@ai-tutor.com / admin123!@#
- **기관 관리자**: institution@ai-tutor.com / inst123!
- **일반 사용자**: user@ai-tutor.com / user123!

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
    role ENUM('user', 'institution_admin', 'super_admin') NOT NULL DEFAULT 'user',
    institution_id VARCHAR(100) DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE,
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
- [x] Docker Compose 환경 설정
- [x] MySQL 데이터베이스 스키마 생성
- [x] Qdrant 벡터 DB 초기 설정
- [x] FastAPI 기본 프로젝트 구조 생성
- [x] React 프로젝트 초기화

### Phase 2: 핵심 백엔드 개발 (3주)
- [x] 사용자 인증 시스템 구현
- [x] 채팅 API 엔드포인트 개발
- [x] AI 서비스 통합 (Claude API)
- [x] RAG 시스템 구현 (LangChain + LangGraph + Qdrant)
- [x] 벡터 검색 기능 구현

### Phase 3: 프론트엔드 개발 (3주)
- [x] 로그인/회원가입 UI
- [x] 채팅 인터페이스 구현
- [x] 대시보드 및 학습 진도 표시
- [x] 관리자 UI 기본 구조 생성
- [x] RAG 문서 관리 인터페이스 구현
- [x] 실시간 통신 구현 (WebSocket, SSE)
- [x] 반응형 디자인 적용

### Phase 4: 통합 및 최적화 (2주)
- [x] 전체 시스템 통합 테스트 (2025-06-25 완료)
  - Docker 환경 빌드 및 실행 완료
  - 인증 시스템 테스트 완료
  - AI 채팅 기능 테스트 완료
  - 관리자 기능 테스트 완료
  - RAG 문서 업로드 테스트 완료
  - 리포트 생성 기능 테스트 완료
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
  - RAG 시스템 구현 (LangChain + LangGraph)
- [x] 관리자 시스템 구현 (기본 구조)
  - [x] 관리자 프론트엔드 기본 구조 개발
  - [x] AdminLayout 및 AdminRoute 구현
  - [x] 관리자 대시보드 페이지 구현
  - [x] RAG 문서 관리 인터페이스 구현
  - [x] RAG API 백엔드 연동
    - 문서 목록 조회
    - 문서 업로드 (파일/텍스트)
    - 문서 삭제
    - 실시간 업로드 상태 표시
  - [x] 3단계 권한 시스템 구현
    - UserRole enum 구현 (user, institution_admin, super_admin)
    - 권한별 dependency 함수 구현
    - 데이터베이스 스키마 업데이트 (role, institution_id 컬럼 추가)
    - 초기 관리자 계정 생성 (admin@ai-tutor.com / admin123!@#)
    - 관리자 전용 로그인 제거 (통합 인증 시스템 사용)
  - [x] 사용자 관리 페이지 업데이트
    - 사용자 목록 조회 및 필터링
    - 사용자 상태 토글 (활성/비활성)
    - 3단계 권한 변경 기능 (일반/기관관리자/슈퍼관리자)
    - 사용자 상세 정보 모달
    - 기관 ID 표시 (기관 관리자용)
  - [x] 통계 분석 페이지 구현
    - 사용자 분석 (권한별 분포, 신규 가입자 추이)
    - 학습 분석 (평균 대화 길이, 학습 시간, 완료율)
    - 사용량 분석 (시간대별 사용량, API 사용량)
    - 날짜 범위 선택 기능
  - [x] 시스템 설정 페이지 구현
    - 일반 설정 (사이트 정보, 유지보수 모드)
    - AI 설정 (모델 선택, 파라미터 설정)
    - 보안 설정 (비밀번호 정책, 2단계 인증)
    - 알림 설정 (이메일, Slack)
    - 저장소 설정 (파일 크기, 할당량)
    - 유지보수 기능 (캐시 삭제, DB 백업)
  - [x] 관리자 API 엔드포인트 추가 개발
  - [x] RBAC 권한 시스템 구현
  - [x] 콘텐츠 관리 시스템 구현
    - Content/ContentCategory 데이터베이스 모델 생성
    - Content CRUD API 엔드포인트 구현
    - ContentPage 컴포넌트 (목록, 필터링, 검색)
    - ContentEditor 컴포넌트 (마크다운 편집기, SEO 설정)
    - CategoryManager 컴포넌트 (계층적 카테고리 관리)
    - 발행/보관 기능 구현
  - [x] 실시간 기능 구현
    - WebSocket 서버 구현 (채팅, 사용자 활동)
    - 채팅 메시지 스트리밍 (SSE 방식)
    - 실시간 연결 관리
  - [x] 시스템 모니터링 대시보드
    - MonitoringPage 구현
    - 실시간 시스템 메트릭 표시
    - 서비스 상태 모니터링
    - 활동 로그 표시
  - [x] 학습 경로 시각화
    - LearningPathVisualization 컴포넌트
    - 레벨별 노드 표시
    - 진행 상태 시각화 (완료/진행중/잠김)
    - 스킬 및 포인트 시스템
  - [x] 리포트 생성 시스템
    - Report 데이터베이스 모델 생성
    - 리포트 생성 API 엔드포인트
    - ReportsPage 구현 (리포트 유형 선택, 파라미터 설정)
    - 리포트 목록 및 다운로드 기능
    - 리포트 진행 상태 추적
- [x] 리포트 실제 생성 기능
  - [x] 백그라운드 작업 시스템 (Celery)
    - Celery worker 설정 및 Docker Compose 통합
    - Redis를 브로커로 사용
    - 작업 진행 상태 추적
  - [x] PDF/Excel/CSV 파일 생성
    - ReportLab을 사용한 PDF 생성
    - XlsxWriter를 사용한 Excel 생성
    - Pandas를 사용한 CSV 생성
  - [x] 리포트 템플릿 시스템
    - 사용자 진도 리포트
    - 학습 분석 리포트
    - AI 도구 사용 현황
    - 월간 종합 리포트
    - 맞춤형 리포트
  - [x] 리포트 진행 상태 모달
    - 실시간 진행률 표시
    - 완료/실패 상태 알림
- [x] 통합 테스트 및 이슈 해결 (2025-06-25)
  - [x] Redis 연결 이슈 해결 (localhost → container name)
  - [x] ReportType enum 이름 오류 수정
  - [x] 환경 변수 설정 수정 (.env 파일)
  - [x] 모든 핵심 기능 정상 작동 확인
- [ ] 한글 폰트 지원 (PDF)
- [ ] 배포 준비
- [ ] 실시간 모니터링 대시보드 강화
- [ ] AI 모델 파인튜닝 및 최적화
- [ ] 기관별 맞춤형 설정 기능
- [ ] 모바일 앱 개발 (React Native)
- [ ] API 문서화 및 SDK 개발
- [ ] 다국어 지원 (영어, 중국어, 일본어)
- [ ] 고급 분석 및 인사이트 기능
- [ ] 외부 LMS 연동 기능

**최종 업데이트**: 2025-06-25 17:40

## 통합 테스트 결과 요약 (2025-06-25)

### 테스트 환경
- Docker Compose로 모든 서비스 실행
- 총 7개 컨테이너: MySQL, Redis, Qdrant, Backend, Frontend, AI Service, Celery Worker

### 테스트 결과
1. **인증 시스템**: ✅ 회원가입, 로그인, JWT 토큰 발급 정상 작동
2. **AI 채팅**: ✅ 대화 생성, 메시지 전송/응답 정상 (평균 응답 시간 30초)
3. **관리자 기능**: ✅ 대시보드 통계, 권한별 접근 제어 정상
4. **RAG 시스템**: ✅ 문서 업로드 및 벡터화 성공
5. **리포트 생성**: ✅ Excel 리포트 생성 및 다운로드 성공

### 해결된 이슈
1. **Celery Redis 연결 문제**: 환경 변수에서 localhost를 컨테이너 이름으로 변경
2. **ReportType Enum 오류**: 스키마와 모델 간 enum 이름 일치
3. **datetime 직렬화 문제**: 스키마에서 날짜 필드를 문자열로 변경

### 남은 작업
- PDF 한글 폰트 지원
- 성능 최적화
- 프로덕션 배포 준비
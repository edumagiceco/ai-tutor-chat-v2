# AI Tutor System (chat-v2)

성인 학습자를 위한 AI 기반 교육 챗봇 시스템입니다. 직장인들이 AI 도구를 활용하여 업무 효율성을 높일 수 있도록 맞춤형 학습 경로와 실시간 대화형 지원을 제공합니다.

## 주요 기능

- **AI 대화형 학습**: Claude API를 활용한 자연스러운 대화형 학습 지원
- **맞춤형 학습 경로**: 사용자의 직무와 수준에 맞는 개인화된 학습 경로 제공
- **실무 중심 교육**: 즉시 업무에 적용 가능한 AI 도구 활용법 교육
- **학습 진도 관리**: 개인별 학습 진도 추적 및 성과 분석

## 기술 스택

### Backend
- **FastAPI** (Python 3.11): 고성능 비동기 웹 프레임워크
- **MySQL 8.0**: 관계형 데이터베이스
- **Redis**: 캐싱 및 세션 관리
- **Qdrant**: 벡터 데이터베이스 (RAG 시스템용)

### Frontend
- **React 19** with TypeScript
- **Tailwind CSS 3.4**: 유틸리티 기반 CSS 프레임워크
- **React Query**: 서버 상태 관리

### AI/ML
- **Anthropic Claude API**: 메인 대화 엔진
- **OpenAI Embeddings API**: 텍스트 임베딩 생성

### Infrastructure
- **Docker Compose**: 로컬 개발 환경
- **JWT**: 인증 시스템

## 시작하기

### 필수 요구사항
- Docker & Docker Compose
- Anthropic API Key
- OpenAI API Key

### 설치 및 실행

1. 저장소 클론
```bash
git clone [repository-url]
cd ai-tutor
```

2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일에 API 키 입력
```

3. Docker Compose로 실행
```bash
docker-compose up -d
```

4. 서비스 접속
- Frontend: http://localhost:3000
- Backend API: http://localhost:8081
- API 문서: http://localhost:8081/docs

### 테스트 계정
- 이메일: test@example.com
- 비밀번호: secret

## 프로젝트 구조

```
ai-tutor/
├── backend/          # FastAPI 백엔드 서버
├── frontend/         # React 프론트엔드
├── ai-service/       # AI 처리 마이크로서비스
├── sql/              # 데이터베이스 초기화 스크립트
├── docs/             # 프로젝트 문서
└── docker-compose.yml
```

## 개발 현황

현재 구현된 기능:
- ✅ 사용자 인증 시스템 (JWT 기반)
- ✅ AI 채팅 인터페이스
- ✅ 학습 관리 시스템
- ✅ 사용자 프로필 관리
- ✅ 한글 UTF-8 인코딩 지원

개발 예정:
- 관리자 대시보드
- RAG 시스템 고도화
- 학습 분석 및 리포트
- 팀 단위 학습 관리

## 라이선스

이 프로젝트는 비공개 소프트웨어입니다.
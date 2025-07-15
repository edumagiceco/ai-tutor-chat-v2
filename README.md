# AI Tutor System - 성인 대상 AI 역량 기반 업무혁신 교육 챗봇

## 프로젝트 개요

AI Tutor System은 성인 학습자의 AI 역량 개발을 통한 업무 혁신을 지원하는 교육 챗봇 시스템입니다. 직장인, 전문가, 관리자를 대상으로 실무 적용성이 높은 개인화된 학습 경로를 제공합니다.

### 주요 특징
- 🎯 실무 중심의 AI 교육 콘텐츠
- 🤖 Claude AI 기반 지능형 대화 시스템
- 📊 개인별 맞춤형 학습 경로
- 📈 실시간 학습 진도 추적
- 🔐 3단계 권한 시스템 (사용자/기관관리자/슈퍼관리자)
- 📋 종합적인 리포트 생성 기능

## 시스템 아키텍처

### 기술 스택
- **Frontend**: React.js 18 + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI + SQLAlchemy
- **AI Service**: Anthropic Claude API + OpenAI Embeddings
- **Database**: MySQL 8.0 + Redis + Qdrant (Vector DB)
- **Infrastructure**: Docker Compose
- **Background Tasks**: Celery + Redis

## 시작하기

### 사전 요구사항
- Docker & Docker Compose
- Node.js 18+ (개발용)
- Python 3.11+ (개발용)

### 환경 설정

1. 저장소 클론
```bash
git clone https://github.com/MagicecoleAI/ai-tutor.git
cd ai-tutor
```

2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 필요한 API 키 입력
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

3. Docker 컨테이너 실행
```bash
docker-compose up -d
```

4. 초기 데이터베이스 설정 확인
```bash
docker logs ai-tutor-mysql-1
```

## Windows에서 Docker Hub 이미지로 실행하기 (Intel/AMD64)

### 사전 요구사항
- Windows 10/11 (64bit)
- Docker Desktop for Windows 설치
- WSL2 활성화 (권장)

### 실행 방법

1. **프로젝트 다운로드**
```powershell
git clone https://github.com/MagicecoleAI/ai-tutor.git
cd ai-tutor
```

2. **환경 변수 파일 생성**
```powershell
# PowerShell에서 실행
copy .env.example .env

# .env 파일을 메모장으로 열어 API 키 설정
notepad .env
```

필수 환경 변수:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
MYSQL_ROOT_PASSWORD=your_mysql_root_password
JWT_SECRET=your_jwt_secret_key_here
```

3. **Docker Hub 이미지를 사용한 실행**

Production 환경:
```powershell
docker-compose -f docker-compose.prod.yml up -d
```

Staging 환경 (테스트용):
```powershell
docker-compose -f docker-compose.staging.yml up -d
```

4. **실행 확인**
```powershell
# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

5. **시스템 접속**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8081
- API Documentation: http://localhost:8081/docs
- AI Service: http://localhost:8000/docs

### Windows 환경 특별 주의사항

1. **Docker Desktop 설정**
   - Settings → Resources → WSL Integration 활성화
   - Settings → Resources → Advanced에서 충분한 메모리 할당 (최소 8GB 권장)

2. **방화벽 설정**
   - Windows Defender 방화벽에서 Docker Desktop 허용
   - 필요시 포트 3000, 8081, 8000, 3307, 6379, 6333 열기

3. **디스크 공간**
   - 최소 20GB 여유 공간 필요
   - Docker 이미지 저장 위치 확인: Settings → Resources → Disk image location

4. **성능 최적화**
   - WSL2 사용 권장 (Hyper-V보다 성능 우수)
   - Windows 실시간 보호에서 Docker 폴더 제외

### 문제 해결 (Windows)

1. **컨테이너가 시작되지 않을 때**
```powershell
# Docker Desktop 재시작
# 시스템 트레이에서 Docker 아이콘 우클릭 → Restart

# WSL 재시작
wsl --shutdown
```

2. **포트 충돌 문제**
```powershell
# 포트 사용 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8081

# 필요시 docker-compose.prod.yml에서 포트 변경
```

3. **MySQL 연결 문제**
   - Windows에서는 localhost 대신 127.0.0.1 사용 권장
   - MySQL Workbench로 연결 테스트: 127.0.0.1:3307

### 서비스 중지
```powershell
# Production 환경 중지
docker-compose -f docker-compose.prod.yml down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose -f docker-compose.prod.yml down -v
```

### 접속 정보

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8081
- **API Documentation**: http://localhost:8081/docs
- **AI Service**: http://localhost:8000/docs

### 테스트 계정 정보

#### 권한별 계정 목록

1. **슈퍼 관리자 (Super Admin)**
   - 이메일: `admin@ai-tutor.com`
   - 비밀번호: `admin123!@#`
   - 권한: 전체 시스템 관리, 모든 기능 접근 가능

2. **기관 관리자 (Institution Admin)**
   - 이메일: `institution@ai-tutor.com`
   - 비밀번호: `inst123!`
   - 권한: 소속 기관 사용자 관리, 기관별 설정

3. **일반 사용자 (User)**
   - 이메일: `user@ai-tutor.com`
   - 비밀번호: `user123!`
   - 권한: AI 채팅, 학습 기능 사용

## 주요 기능

### 사용자 시스템
- AI 기반 대화형 학습
- 개인별 학습 경로 관리
- 실시간 진도 추적
- AI 도구 추천 시스템

### 관리자 시스템
- 사용자 관리 및 권한 설정
- RAG 문서 관리
- 학습 콘텐츠 관리
- 통계 분석 대시보드
- 리포트 생성 (PDF/Excel/CSV)

### AI 기능
- 자연어 이해 및 응답
- 컨텍스트 기반 대화
- RAG 기반 지식 검색
- 학습 패턴 분석

## 개발 가이드

### 로컬 개발 환경

1. Backend 개발
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8081
```

2. Frontend 개발
```bash
cd frontend
npm install
npm start
```

3. AI Service 개발
```bash
cd ai-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 코드 구조

```
ai-tutor/
├── frontend/           # React 프론트엔드
│   ├── src/
│   │   ├── components/ # UI 컴포넌트
│   │   ├── pages/     # 페이지 컴포넌트
│   │   ├── contexts/  # React Context
│   │   └── services/  # API 통신
├── backend/           # FastAPI 백엔드
│   ├── app/
│   │   ├── api/      # API 엔드포인트
│   │   ├── models/   # 데이터베이스 모델
│   │   ├── services/ # 비즈니스 로직
│   │   └── core/     # 핵심 설정
├── ai-service/       # AI 마이크로서비스
│   └── app/
│       ├── api/      # AI API
│       └── core/     # AI 엔진
└── docs/            # 프로젝트 문서
```

## API 엔드포인트

### 인증
- POST `/api/v1/auth/signup` - 회원가입
- POST `/api/v1/auth/login` - 로그인
- POST `/api/v1/auth/logout` - 로그아웃
- GET `/api/v1/auth/me` - 현재 사용자 정보

### 채팅
- POST `/api/v1/chat/conversations` - 새 대화 생성
- POST `/api/v1/chat/conversations/{id}/messages` - 메시지 전송
- GET `/api/v1/chat/conversations` - 대화 목록 조회

### 학습 관리
- GET `/api/v1/learning/path` - 학습 경로 조회
- PUT `/api/v1/learning/progress` - 진도 업데이트
- GET `/api/v1/learning/recommendations` - AI 도구 추천

### 관리자
- GET `/api/v1/admin/users` - 사용자 목록
- PUT `/api/v1/admin/users/{id}` - 사용자 정보 수정
- POST `/api/v1/admin/reports` - 리포트 생성

## 문제 해결

### Docker 관련
```bash
# 모든 컨테이너 재시작
docker-compose restart

# 특정 서비스 로그 확인
docker logs ai-tutor-backend-1 -f

# 컨테이너 재빌드
docker-compose build --no-cache
```

### 데이터베이스 관련
```bash
# MySQL 접속
docker exec -it ai-tutor-mysql-1 mysql -u magic7 -p

# Redis CLI
docker exec -it ai-tutor-redis-1 redis-cli
```

## 보안 고려사항

- 모든 API 키는 환경 변수로 관리
- JWT 기반 인증 시스템
- CORS 설정으로 허용된 출처만 접근
- SQL Injection 방지 (SQLAlchemy ORM)
- Rate Limiting 적용

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 문의사항

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.

---

Made with ❤️ by AI Education Team
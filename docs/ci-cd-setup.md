# AI Tutor System CI/CD 설정 가이드

## 개요

이 문서는 AI Tutor System의 GitHub Actions 기반 CI/CD 파이프라인 설정 방법을 설명합니다.

## 필요한 GitHub Secrets 설정

GitHub 리포지토리의 Settings → Secrets and variables → Actions에서 다음 시크릿을 설정해야 합니다:

### 1. 환경 변수
- `ANTHROPIC_API_KEY`: Anthropic Claude API 키
- `OPENAI_API_KEY`: OpenAI API 키
- `JWT_SECRET_KEY`: JWT 토큰 서명용 시크릿 키
- `DB_PASSWORD`: 데이터베이스 패스워드
- `MYSQL_ROOT_PASSWORD`: MySQL root 패스워드

### 2. 스테이징 서버 정보
- `STAGING_HOST`: 스테이징 서버 IP 또는 도메인
- `STAGING_USER`: SSH 접속 사용자명
- `STAGING_SSH_KEY`: SSH 개인키

### 3. 프로덕션 서버 정보
- `PRODUCTION_HOST`: 프로덕션 서버 IP 또는 도메인
- `PRODUCTION_USER`: SSH 접속 사용자명
- `PRODUCTION_SSH_KEY`: SSH 개인키

### 4. 모니터링 및 알림
- `SLACK_WEBHOOK`: Slack 웹훅 URL (선택사항)
- `GRAFANA_USER`: Grafana 관리자 사용자명
- `GRAFANA_PASSWORD`: Grafana 관리자 비밀번호

## CI/CD 워크플로우

### 1. 코드 품질 검사 (Code Quality)
- Python: flake8, black, isort, mypy
- JavaScript: ESLint
- 모든 PR과 푸시에서 자동 실행

### 2. 테스트 실행 (Testing)
- Backend: pytest + coverage
- Frontend: Jest + React Testing Library
- 테스트 커버리지 리포트 생성

### 3. 보안 스캔 (Security)
- Bandit: Python 보안 취약점 스캔
- Safety: 의존성 취약점 검사
- Trivy: 컨테이너 이미지 스캔
- npm audit: JavaScript 패키지 취약점 검사
- TruffleHog: 시크릿 노출 검사

### 4. Docker 이미지 빌드
- 멀티 서비스 동시 빌드 (병렬 처리)
- GitHub Container Registry (ghcr.io) 사용
- 브랜치별 태깅 전략:
  - `main`: production 태그
  - `develop`: staging 태그
  - PR: pr-{number} 태그

### 5. 배포 프로세스

#### 스테이징 배포 (develop 브랜치)
1. develop 브랜치 푸시 시 자동 트리거
2. Docker 이미지 pull
3. docker-compose.staging.yml로 서비스 재시작
4. 헬스 체크 수행

#### 프로덕션 배포 (main 브랜치)
1. main 브랜치 푸시 시 자동 트리거
2. 수동 승인 필요 (environment protection)
3. Docker 이미지 pull
4. 블루-그린 배포 방식
5. 헬스 체크 및 롤백 준비
6. Slack 알림 발송

## 서버 초기 설정

### 1. Docker 및 Docker Compose 설치
```bash
# Ubuntu 서버 기준
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 프로젝트 디렉토리 생성
```bash
sudo mkdir -p /home/ubuntu/ai-tutor
sudo chown -R ubuntu:ubuntu /home/ubuntu/ai-tutor
cd /home/ubuntu/ai-tutor
git clone https://github.com/MagicecoleAI/ai-tutor.git .
```

### 3. 환경 변수 파일 생성
```bash
# .env 파일 생성 (본 예제 참고)
cp .env.example .env
# 실제 값으로 편집
nano .env
```

### 4. SSL 인증서 설정
```bash
# Let's Encrypt 사용
sudo apt install certbot
sudo certbot certonly --standalone -d ai-tutor.com -d www.ai-tutor.com -d api.ai-tutor.com

# 인증서 복사
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/ai-tutor.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/ai-tutor.com/privkey.pem nginx/ssl/
```

## 로컬 개발 환경에서 CI/CD 테스트

### 1. GitHub Actions 로컬 실행
```bash
# act 설치 (macOS)
brew install act

# 워크플로우 실행
act -j code-quality
act -j test
```

### 2. Docker 이미지 로컬 빌드
```bash
# 개별 서비스 빌드
docker build -t ai-tutor-backend:local ./backend
docker build -t ai-tutor-frontend:local ./frontend

# Docker Compose로 전체 빌드
docker-compose build
```

## 모니터링 및 로깅

### 1. Prometheus + Grafana
- Prometheus: 메트릭 수집
- Grafana: 시각화 대시보드
- 접속: http://your-server:3000 (Grafana)

### 2. 로그 수집
```bash
# 모든 컨테이너 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
```

### 3. 헬스 체크 엔드포인트
- Frontend: http://localhost:3000/health
- Backend: http://localhost:8081/health
- AI Service: http://localhost:8000/health

## 트러블슈팅

### 1. 빌드 실패
- Docker 데몬 실행 확인
- 디스크 공간 확인
- 네트워크 연결 확인

### 2. 배포 실패
- SSH 키 권한 확인 (600)
- 서버 디스크 공간 확인
- Docker 서비스 상태 확인

### 3. 테스트 실패
- 데이터베이스 연결 확인
- 환경 변수 설정 확인
- 의존성 버전 충돌 확인

## 베스트 프랙티스

1. **브랜치 전략**
   - main: 프로덕션 배포
   - develop: 스테이징 배포
   - feature/*: 기능 개발
   - hotfix/*: 긴급 수정

2. **커밋 메시지**
   - feat: 새로운 기능
   - fix: 버그 수정
   - docs: 문서 수정
   - style: 코드 포맷팅
   - refactor: 코드 리팩토링
   - test: 테스트 추가
   - chore: 빌드 업무 수정

3. **보안**
   - 시크릿은 절대 코드에 포함하지 않음
   - 정기적인 의존성 업데이트
   - 보안 스캔 결과 즉시 대응

4. **성능**
   - Docker 이미지 최소화
   - 멀티 스테이지 빌드 활용
   - 캐시 적극 활용

## 추가 리소스

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Docker 공식 문서](https://docs.docker.com)
- [Prometheus 모니터링 가이드](https://prometheus.io/docs)

---

최종 업데이트: 2025-06-25
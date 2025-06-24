# 사용자 챗봇 시스템 상세 기획서

## 1. 시스템 개요

### 1.1 목적
성인 학습자가 AI 도구를 활용하여 업무 혁신을 이룰 수 있도록 지원하는 대화형 교육 챗봇 시스템

### 1.2 핵심 가치
- **맞춤형 학습**: 직무별, 레벨별 개인화된 학습 경로
- **실무 중심**: 즉시 업무에 적용 가능한 AI 스킬 습득
- **대화형 학습**: 자연스러운 대화를 통한 학습 지원

## 2. 주요 기능

### 2.1 사용자 인증 및 프로필

#### 2.1.1 회원가입/로그인
```
화면 구성:
- 이메일/비밀번호 입력
- 소셜 로그인 (Google, Microsoft)
- 직무 정보 입력
  * 업종 선택 (IT, 마케팅, 영업, 인사, 재무 등)
  * 직급 (사원, 대리, 과장, 차장, 부장 등)
  * AI 활용 경험 수준 (초급, 중급, 고급)
```

#### 2.1.2 사용자 프로필 관리
```
프로필 정보:
- 기본 정보 (이름, 이메일, 프로필 사진)
- 직무 정보 (부서, 직급, 주요 업무)
- AI 스킬 레벨 (자동 평가 + 수동 설정)
- 학습 목표 설정
- 관심 AI 도구 선택
```

### 2.2 AI 챗봇 인터페이스

#### 2.2.1 메인 채팅 화면
```
구성 요소:
1. 대화 영역
   - 메시지 버블 (사용자/AI)
   - 타이핑 인디케이터
   - 메시지 타임스탬프
   - 코드 블록 하이라이팅
   - 이미지/파일 업로드 지원

2. 입력 영역
   - 텍스트 입력창
   - 파일 첨부 버튼
   - 음성 입력 버튼
   - 전송 버튼

3. 사이드바
   - 대화 히스토리
   - 학습 진도
   - 빠른 액션 메뉴
```

#### 2.2.2 대화 유형별 기능
```
1. 학습 질문
   - AI 개념 설명 요청
   - 도구 사용법 문의
   - 실습 예제 요청

2. 문제 해결
   - 업무 시나리오 제시
   - AI 솔루션 추천
   - 단계별 가이드 제공

3. 실습 모드
   - 프롬프트 작성 연습
   - AI 도구 시뮬레이션
   - 결과 분석 및 피드백
```

### 2.3 학습 관리 시스템

#### 2.3.1 학습 경로 (Learning Path)
```
화면 구성:
1. 현재 레벨 표시
   - 시각적 프로그레스 바
   - 달성 배지
   - 다음 목표 안내

2. 추천 학습 콘텐츠
   - 다음 학습 주제
   - 예상 소요 시간
   - 난이도 표시

3. 학습 로드맵
   - 전체 커리큘럼 뷰
   - 완료/진행중/예정 표시
   - 예상 완료 시간
```

#### 2.3.2 AI 도구 라이브러리
```
기능:
1. 도구 카탈로그
   - 카테고리별 분류
   - 난이도별 필터
   - 인기도/평점

2. 도구 상세 정보
   - 기능 설명
   - 사용 가이드
   - 실습 예제
   - 관련 튜토리얼

3. 즐겨찾기
   - 자주 사용하는 도구
   - 학습 예정 도구
```

### 2.4 실습 및 프로젝트

#### 2.4.1 가이드 실습
```
구성:
1. 시나리오 기반 실습
   - 실제 업무 상황 제시
   - 단계별 가이드
   - 힌트 시스템
   - 정답 확인

2. 실습 유형
   - ChatGPT 프롬프트 작성
   - 이미지 생성 AI 활용
   - 데이터 분석 자동화
   - 문서 작성 효율화
```

#### 2.4.2 개인 프로젝트
```
기능:
1. 프로젝트 생성
   - 목표 설정
   - 사용할 AI 도구 선택
   - 예상 결과물 정의

2. 진행 관리
   - 체크리스트
   - 진도 추적
   - AI 멘토링

3. 결과 공유
   - 포트폴리오 생성
   - 동료 피드백
   - 성과 인증
```

### 2.5 성과 및 분석

#### 2.5.1 학습 대시보드
```
주요 지표:
1. 학습 통계
   - 총 학습 시간
   - 완료한 과정 수
   - 습득한 AI 도구

2. 스킬 매트릭스
   - 역량별 레벨 차트
   - 성장 추이 그래프
   - 동료 대비 순위

3. 업무 적용 성과
   - 적용 사례 수
   - 시간 절감 효과
   - 생산성 향상도
```

#### 2.5.2 인증 및 배지
```
인증 시스템:
1. 스킬 배지
   - 도구별 숙련도
   - 레벨별 인증
   - 특별 성취

2. 수료증
   - 과정 수료증
   - 프로젝트 완료증
   - 연간 성과 인증
```

## 3. 기술적 구현

### 3.1 프론트엔드 아키텍처

```
frontend/
├── src/
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   └── ProfileSetupPage.tsx
│   │   ├── chat/
│   │   │   ├── ChatPage.tsx
│   │   │   ├── ConversationList.tsx
│   │   │   └── MessageArea.tsx
│   │   ├── learning/
│   │   │   ├── LearningPathPage.tsx
│   │   │   ├── ToolLibraryPage.tsx
│   │   │   └── PracticePage.tsx
│   │   └── dashboard/
│   │       ├── DashboardPage.tsx
│   │       ├── ProgressChart.tsx
│   │       └── AchievementList.tsx
│   ├── components/
│   │   ├── chat/
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── InputArea.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   └── VoiceInput.tsx
│   │   ├── learning/
│   │   │   ├── ProgressBar.tsx
│   │   │   ├── SkillCard.tsx
│   │   │   └── ToolCard.tsx
│   │   └── common/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Modal.tsx
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useAuth.ts
│   │   └── useLearning.ts
│   └── services/
│       ├── api/
│       │   ├── authApi.ts
│       │   ├── chatApi.ts
│       │   └── learningApi.ts
│       └── websocket.ts
```

### 3.2 상태 관리

```typescript
// Redux Store 구조
interface AppState {
  auth: {
    user: User | null;
    isAuthenticated: boolean;
    loading: boolean;
  };
  chat: {
    conversations: Conversation[];
    currentConversation: Conversation | null;
    messages: Message[];
    isTyping: boolean;
  };
  learning: {
    learningPath: LearningPath | null;
    progress: Progress;
    achievements: Achievement[];
    recommendations: Recommendation[];
  };
}
```

### 3.3 API 엔드포인트

```yaml
# 사용자 인증
POST   /api/v1/auth/signup
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
PUT    /api/v1/auth/profile

# 채팅
POST   /api/v1/chat/conversations
GET    /api/v1/chat/conversations
GET    /api/v1/chat/conversations/{id}
POST   /api/v1/chat/conversations/{id}/messages
DELETE /api/v1/chat/conversations/{id}

# 학습 관리
GET    /api/v1/learning/path
PUT    /api/v1/learning/path/progress
GET    /api/v1/learning/tools
GET    /api/v1/learning/tools/{id}
POST   /api/v1/learning/tools/{id}/favorite

# 실습 및 프로젝트
GET    /api/v1/practice/scenarios
POST   /api/v1/practice/submit
GET    /api/v1/projects
POST   /api/v1/projects
PUT    /api/v1/projects/{id}

# 성과 분석
GET    /api/v1/analytics/dashboard
GET    /api/v1/analytics/skills
GET    /api/v1/achievements
```

## 4. UI/UX 디자인 가이드

### 4.1 디자인 원칙
- **직관성**: 복잡한 AI 개념을 쉽게 이해
- **일관성**: 통일된 디자인 시스템
- **접근성**: WCAG 2.1 AA 준수
- **반응형**: 모바일/태블릿/데스크톱 지원

### 4.2 컬러 시스템
```css
:root {
  --primary: #2563EB;      /* 신뢰감 있는 블루 */
  --secondary: #7C3AED;    /* 혁신적인 퍼플 */
  --success: #10B981;      /* 성취감 그린 */
  --warning: #F59E0B;      /* 주의 오렌지 */
  --error: #EF4444;        /* 에러 레드 */
  --neutral: #6B7280;      /* 중립 그레이 */
}
```

### 4.3 타이포그래피
```css
/* 본문: Inter, Noto Sans KR */
/* 코드: Fira Code, D2Coding */
/* 제목: Pretendard, Inter */
```

## 5. 보안 및 개인정보 보호

### 5.1 인증 보안
- JWT 토큰 기반 인증
- Refresh Token 구현
- 2FA 옵션 제공

### 5.2 데이터 보호
- 대화 내용 암호화 저장
- 개인정보 마스킹
- GDPR 준수

## 6. 성능 최적화

### 6.1 프론트엔드
- 코드 스플리팅
- 이미지 레이지 로딩
- 서비스 워커 캐싱

### 6.2 백엔드
- Redis 캐싱
- 데이터베이스 쿼리 최적화
- CDN 활용

**최종 업데이트**: 2025-06-24
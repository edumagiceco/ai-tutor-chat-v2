# 관리자 시스템 상세 기획서

## 1. 시스템 개요

### 1.1 목적
AI 교육 챗봇 시스템의 운영, 콘텐츠 관리, 사용자 분석, 시스템 모니터링을 위한 통합 관리 플랫폼

### 1.2 주요 사용자
- 시스템 관리자
- 콘텐츠 매니저
- 교육 담당자
- 데이터 분석가

## 2. 주요 기능

### 2.1 대시보드

#### 2.1.1 메인 대시보드
```
주요 위젯:
1. 실시간 지표
   - 현재 활성 사용자 수
   - 오늘의 대화 수
   - 시스템 상태 (CPU, Memory, API 응답시간)
   - AI API 사용량 및 비용

2. 핵심 통계
   - 일간/주간/월간 사용자 증가율
   - 평균 학습 시간
   - 인기 AI 도구 TOP 10
   - 사용자 만족도 점수

3. 알림 센터
   - 시스템 에러 알림
   - API 한도 경고
   - 이상 패턴 감지
   - 중요 사용자 피드백
```

#### 2.1.2 분석 대시보드
```
분석 항목:
1. 사용자 분석
   - 직무별 분포
   - 레벨별 진도
   - 이탈률 분석
   - 코호트 분석

2. 학습 효과 분석
   - 과정별 완료율
   - 평균 학습 시간
   - 재방문율
   - 성과 향상도

3. AI 사용 분석
   - 모델별 사용량
   - 평균 응답 시간
   - 오류율
   - 비용 분석
```

### 2.2 사용자 관리

#### 2.2.1 사용자 목록 및 검색
```
기능:
1. 사용자 검색
   - 이름, 이메일, 직무별 필터
   - 가입일, 최근 접속일 정렬
   - 활성/비활성 상태 필터

2. 사용자 상세 정보
   - 프로필 정보
   - 학습 진도
   - 대화 히스토리
   - 활동 로그

3. 사용자 관리 액션
   - 계정 활성화/비활성화
   - 비밀번호 초기화
   - 권한 변경
   - 학습 경로 수정
```

#### 2.2.2 그룹 관리
```
기능:
1. 기업/조직 관리
   - 기업별 그룹 생성
   - 대량 사용자 등록
   - 그룹별 설정

2. 학습 그룹
   - 과정별 그룹 생성
   - 멘토 지정
   - 그룹 공지사항
```

### 2.3 콘텐츠 관리

#### 2.3.1 학습 콘텐츠 관리
```
관리 항목:
1. 커리큘럼 편집
   - 학습 경로 설계
   - 모듈 추가/수정/삭제
   - 난이도 설정
   - 선수 과정 지정

2. AI 도구 카탈로그
   - 새 도구 등록
   - 카테고리 관리
   - 사용 가이드 작성
   - 관련 자료 업로드

3. 실습 시나리오
   - 시나리오 작성
   - 정답 및 힌트 설정
   - 평가 기준 정의
```

#### 2.3.2 RAG 데이터 관리
```
기능:
1. 문서 관리
   - 문서 업로드 (PDF, DOCX, TXT)
   - 자동 청킹 및 임베딩
   - 메타데이터 태깅
   - 버전 관리

2. 벡터 DB 관리
   - 컬렉션 생성/삭제
   - 인덱스 최적화
   - 유사도 임계값 조정
   - 검색 테스트

3. 지식베이스 큐레이션
   - 품질 검증
   - 중복 제거
   - 업데이트 스케줄링
```

### 2.4 대화 모니터링

#### 2.4.1 실시간 대화 모니터링
```
기능:
1. 라이브 대화 뷰
   - 진행 중인 대화 목록
   - 실시간 메시지 확인
   - 개입 필요 알림
   - 긴급 지원 요청

2. 대화 품질 관리
   - AI 응답 정확도 평가
   - 부적절한 응답 플래깅
   - 응답 시간 모니터링
   - 오류 대화 추적

3. 피드백 수집
   - 사용자 평가 통계
   - 부정적 피드백 분석
   - 개선 요청 사항
```

#### 2.4.2 대화 분석
```
분석 항목:
1. 주제별 분석
   - 자주 묻는 질문
   - 주제별 분류
   - 트렌드 분석

2. 감정 분석
   - 사용자 만족도
   - 감정 변화 추이
   - 이탈 예측

3. 성과 분석
   - 학습 목표 달성률
   - 문제 해결률
   - 재질문율
```

### 2.5 시스템 설정

#### 2.5.1 AI 모델 설정
```
설정 항목:
1. 모델 파라미터
   - Temperature 조정
   - Max tokens 설정
   - 시스템 프롬프트 관리
   - 모델 버전 선택

2. API 관리
   - API 키 관리
   - 사용량 한도 설정
   - 비용 알림 설정
   - 백업 모델 지정

3. 응답 정책
   - 금지어 설정
   - 응답 가이드라인
   - 안전 필터 레벨
```

#### 2.5.2 시스템 구성
```
관리 항목:
1. 인증 설정
   - SSO 설정
   - 2FA 정책
   - 세션 타임아웃

2. 알림 설정
   - 이메일 템플릿
   - 알림 규칙
   - 에스컬레이션 정책

3. 백업 및 복구
   - 자동 백업 스케줄
   - 복구 지점 관리
   - 데이터 내보내기
```

### 2.6 보고서 및 인사이트

#### 2.6.1 정기 보고서
```
보고서 유형:
1. 일일 운영 보고서
   - 주요 지표 요약
   - 이슈 및 해결 현황
   - 내일 예상 부하

2. 주간 성과 보고서
   - 사용자 성장 분석
   - 학습 성과 요약
   - 개선 제안 사항

3. 월간 종합 보고서
   - ROI 분석
   - 전략적 인사이트
   - 다음 달 계획
```

#### 2.6.2 맞춤형 리포트
```
기능:
1. 리포트 빌더
   - 드래그 앤 드롭 위젯
   - 커스텀 지표 생성
   - 필터 및 기간 설정

2. 자동화
   - 정기 발송 스케줄
   - 수신자 그룹 관리
   - 포맷 선택 (PDF, Excel)
```

## 3. 기술적 구현

### 3.1 관리자 프론트엔드 구조

```
admin-frontend/
├── src/
│   ├── pages/
│   │   ├── dashboard/
│   │   │   ├── MainDashboard.tsx
│   │   │   ├── AnalyticsDashboard.tsx
│   │   │   └── widgets/
│   │   ├── users/
│   │   │   ├── UserListPage.tsx
│   │   │   ├── UserDetailPage.tsx
│   │   │   └── GroupManagePage.tsx
│   │   ├── content/
│   │   │   ├── CurriculumEditor.tsx
│   │   │   ├── ToolCatalog.tsx
│   │   │   └── RAGManager.tsx
│   │   ├── monitoring/
│   │   │   ├── LiveChatMonitor.tsx
│   │   │   ├── ConversationAnalysis.tsx
│   │   │   └── QualityControl.tsx
│   │   ├── settings/
│   │   │   ├── AIModelSettings.tsx
│   │   │   ├── SystemConfig.tsx
│   │   │   └── BackupManager.tsx
│   │   └── reports/
│   │       ├── ReportBuilder.tsx
│   │       └── ReportTemplates.tsx
│   ├── components/
│   │   ├── charts/
│   │   ├── tables/
│   │   └── forms/
│   └── services/
│       └── adminApi.ts
```

### 3.2 관리자 API 엔드포인트

```yaml
# 대시보드
GET    /api/v1/admin/dashboard/stats
GET    /api/v1/admin/dashboard/realtime
GET    /api/v1/admin/analytics/overview

# 사용자 관리
GET    /api/v1/admin/users
GET    /api/v1/admin/users/{id}
PUT    /api/v1/admin/users/{id}
POST   /api/v1/admin/users/bulk
DELETE /api/v1/admin/users/{id}

# 콘텐츠 관리
GET    /api/v1/admin/content/curriculum
POST   /api/v1/admin/content/curriculum
PUT    /api/v1/admin/content/curriculum/{id}
DELETE /api/v1/admin/content/curriculum/{id}

# RAG 관리
POST   /api/v1/admin/rag/documents
GET    /api/v1/admin/rag/collections
POST   /api/v1/admin/rag/reindex
DELETE /api/v1/admin/rag/documents/{id}

# 모니터링
GET    /api/v1/admin/monitoring/conversations
GET    /api/v1/admin/monitoring/quality
POST   /api/v1/admin/monitoring/intervention

# 시스템 설정
GET    /api/v1/admin/settings
PUT    /api/v1/admin/settings
POST   /api/v1/admin/backup
GET    /api/v1/admin/logs

# 보고서
GET    /api/v1/admin/reports
POST   /api/v1/admin/reports/generate
GET    /api/v1/admin/reports/{id}/download
```

### 3.3 권한 관리 (RBAC)

```typescript
enum AdminRole {
  SUPER_ADMIN = 'super_admin',
  CONTENT_MANAGER = 'content_manager', 
  SUPPORT_AGENT = 'support_agent',
  ANALYST = 'analyst'
}

interface AdminPermissions {
  dashboard: ['view', 'edit'];
  users: ['view', 'edit', 'delete'];
  content: ['view', 'create', 'edit', 'delete'];
  monitoring: ['view', 'intervene'];
  settings: ['view', 'edit'];
  reports: ['view', 'create', 'export'];
}
```

## 4. 보안 및 감사

### 4.1 접근 제어
- IP 화이트리스트
- 강화된 2FA (TOTP)
- 세션 관리
- 활동 로깅

### 4.2 감사 추적
- 모든 관리 작업 로깅
- 변경 이력 추적
- 정기 감사 보고서
- 이상 행동 탐지

## 5. 성능 및 확장성

### 5.1 대용량 데이터 처리
- 페이지네이션
- 비동기 처리
- 캐싱 전략
- 인덱싱 최적화

### 5.2 실시간 모니터링
- WebSocket 연결
- 서버 전송 이벤트 (SSE)
- 메시지 큐 활용

**최종 업데이트**: 2025-06-24
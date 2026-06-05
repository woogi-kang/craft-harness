---
name: "Figma to Next.js Usage Guide"
description: "Unified converter with strategy selection (Pro, Ralph Hybrid, Ralph Pure)"
---

# Figma → Next.js Converter Usage Guide

> **v3.2.0** - 통합 오케스트레이터 + 전략 선택 방식

---

## 버전 비교 (v3.2.0)

| 특성 | Pro | Ralph Hybrid | Ralph Pure |
|------|-----|--------------|------------|
| 정확도 목표 | 95%+ | 99%+ | 99%+ |
| 최대 반복 | 10 (5×2) | 30 | 50 |
| 검증 방식 | Dual Agent | Score + Playwright | Promise-based |
| 종료 조건 | 점수 임계값 | 98% 이상 | 완료 선언 |
| 권장 사용 | 프로덕션 | 픽셀퍼펙트 | 복잡한 케이스 |

---

## Quick Start

### 전략 지정 방식

```bash
# Pro 전략 (권장 - 프로덕션용)
@figma-to-nextjs [FIGMA_URL] --strategy pro

# Ralph Hybrid (픽셀퍼펙트 필요시)
@figma-to-nextjs [FIGMA_URL] --strategy ralph-hybrid

# Ralph Pure (최대 자율성)
@figma-to-nextjs [FIGMA_URL] --strategy ralph-pure
```

### 전략 미지정 (선택 프롬프트)

```bash
# 전략을 지정하지 않으면 선택 옵션 제공
@figma-to-nextjs [FIGMA_URL]

# → "어떤 전략을 사용할까요?"
#   [Pro (권장)] [Ralph Hybrid] [Ralph Pure]
```

---

## 사전 준비

### 1. Figma MCP 연결 확인

```bash
# MCP 도구 호출 (bash 명령어 아님)
mcp__figma__whoami
```

### 2. Next.js 프로젝트 준비

```bash
# 새 프로젝트 생성
npx create-next-app@latest my-app --typescript --tailwind --eslint --app
cd my-app

# shadcn/ui 초기화
npx shadcn@latest init

# 권장 의존성
npm install zustand @tanstack/react-query zod react-hook-form
```

### 3. Figma URL 형식

```
https://www.figma.com/design/[FILE_KEY]/[FILE_NAME]?node-id=[NODE_ID]
```

---

## 디렉토리 구조 (v3.2.0)

```
figma-to-nextjs/
├── figma-to-nextjs-unified.md    # 통합 오케스트레이터 (메인)
├── USAGE-GUIDE.md                 # 이 가이드
│
├── references/                    # Progressive Disclosure
│   ├── shared/                    # 공통 참조
│   │   ├── must-rules.md         # 필수 규칙
│   │   ├── scoring-weights.md    # 점수 가중치
│   │   └── auto-fix-levels.md    # L1-L4 분류
│   └── strategies/                # 전략별 차이점
│       ├── strategy-pro.md
│       ├── strategy-ralph-hybrid.md
│       └── strategy-ralph-pure.md
│
├── modular/                       # Phase 파일
│   ├── figma-to-nextjs.md        # (기존 호환)
│   └── phases/
│
├── shared/                        # 공유 유틸리티
│
└── fullstack/                     # (기존 - deprecated)
```

---

## 전략 상세

### Pro 전략

- 2개 에이전트가 병렬로 검증
- Conservative: shadcn/ui 우선
- Experimental: 커스텀 Tailwind 시도

### Ralph Hybrid 전략

- 파일 기반 컨텍스트 유지
- Playwright로 렌더링 스크린샷
- 점수 기반 자동 종료

### Ralph Pure 전략

- 최대 자율성
- work-log.md, todo.md로 상태 관리
- "완료됐다"고 판단하면 종료

---

## MUST Rules (모든 전략 공통)

### 1. Figma 에셋 다운로드

```
✅ 모든 이미지/아이콘을 Figma에서 다운로드
❌ lucide-react, heroicons 등 아이콘 라이브러리 사용 금지
```

### 2. 최소 정확도 임계값

```
Pro: 95% 이상
Ralph Hybrid: 98% 이상 (99% 목표)
Ralph Pure: 98% 이상 (자가 평가)
```

### 3. 빌드 성공 필수

```bash
npm run lint    # 에러 0개
npm run build   # 성공 필수
```

---

## 마이그레이션 가이드

```bash
# Before (v2.x)
@figma-to-nextjs-pro [URL]

# After (v3.2.0)
@figma-to-nextjs [URL] --strategy pro
```

---
name: "Figma to Flutter Usage Guide"
description: "Unified converter with strategy selection (Pro, Ralph Hybrid, Ralph Pure)"
---

# Figma → Flutter Converter Usage Guide

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
@figma-to-flutter [FIGMA_URL] --strategy pro

# Ralph Hybrid (픽셀퍼펙트 필요시)
@figma-to-flutter [FIGMA_URL] --strategy ralph-hybrid

# Ralph Pure (최대 자율성)
@figma-to-flutter [FIGMA_URL] --strategy ralph-pure
```

### 전략 미지정 (선택 프롬프트)

```bash
# 전략을 지정하지 않으면 선택 옵션 제공
@figma-to-flutter [FIGMA_URL]

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

### 2. Flutter 프로젝트 준비

```bash
# 새 프로젝트 생성
flutter create my_app --platforms=ios,android,web
cd my_app

# 권장 의존성
flutter pub add flutter_riverpod go_router flutter_svg cached_network_image

# Dev 의존성
flutter pub add --dev golden_toolkit build_runner
```

### 3. Figma URL 형식

```
https://www.figma.com/design/[FILE_KEY]/[FILE_NAME]?node-id=[NODE_ID]
```

---

## 디렉토리 구조 (v3.2.0)

```
figma-to-flutter/
├── figma-to-flutter-unified.md    # 통합 오케스트레이터 (메인)
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
│   ├── figma-to-flutter.md       # (기존 호환)
│   └── phases/
│       ├── phase-0-project-scan.md
│       ├── phase-1-design-scan.md
│       ├── phase-2-token-extract.md
│       ├── phase-3-widget-mapping.md
│       ├── phase-4-code-generate.md
│       ├── phase-5-asset-process.md
│       ├── phase-6-pixel-perfect.md
│       └── phase-7-responsive.md
│
└── fullstack/                     # (기존 - deprecated)
    ├── figma-to-flutter-pro.md
    ├── figma-to-flutter-ralph-hybrid.md
    ├── figma-to-flutter-ralph-pure.md
    └── skills/
```

---

## 전략 상세

### Pro 전략

```yaml
target_accuracy: 95%+
max_iterations: 10 (5 per agent)
verification: Dual Agent (Conservative + Experimental)
exit_condition: Score threshold
```

**특징**:
- 2개 에이전트가 병렬로 검증
- Conservative: 안정적 수정
- Experimental: 창의적 시도
- 더 좋은 결과 선택

### Ralph Hybrid 전략

```yaml
target_accuracy: 99%+ (98% 최소)
max_iterations: 30
verification: Score + Playwright
exit_condition: 98% 이상 점수
```

**특징**:
- 파일 기반 컨텍스트 유지
- Playwright로 Flutter Web 스크린샷
- 점수 기반 자동 종료

### Ralph Pure 전략

```yaml
target_accuracy: 99%+
max_iterations: 50
verification: Self-assessment
exit_condition: Promise tag
```

**특징**:
- 최대 자율성
- work-log.md, todo.md로 상태 관리
- "완료됐다"고 판단하면 종료

---

## MUST Rules (모든 전략 공통)

### 1. Figma 에셋 다운로드

```
✅ 모든 이미지/아이콘을 Figma에서 다운로드
❌ flutter_icons, font_awesome 등 아이콘 라이브러리 사용 금지
❌ 플레이스홀더 이미지 사용 금지
```

### 2. 최소 정확도 임계값

```
Pro: 95% 이상
Ralph Hybrid: 98% 이상
Ralph Pure: 98% 이상 (자가 평가)
```

### 3. 빌드 성공 필수

```bash
flutter analyze   # 에러 0개
flutter build web # 성공 필수
```

---

## 사용 예시

### 한국어

```
"이 Figma 디자인을 Flutter로 변환해줘"
→ 전략 선택 프롬프트

"Figma를 Flutter로 변환해줘 (pro 전략)"
→ Pro 전략으로 즉시 실행

"Ralph 방식으로 완벽하게 변환해줘"
→ Ralph Hybrid 전략으로 실행
```

### English

```
"Convert this Figma design to Flutter"
→ Strategy selection prompt

"Convert using pro strategy"
→ Execute with Pro strategy

"Convert with ralph-pure for maximum accuracy"
→ Execute with Ralph Pure strategy
```

---

## 마이그레이션 가이드

### 기존 에이전트 사용자

```bash
# Before (v2.x)
@figma-to-flutter-pro [URL]
@figma-to-flutter-ralph-hybrid [URL]

# After (v3.2.0)
@figma-to-flutter [URL] --strategy pro
@figma-to-flutter [URL] --strategy ralph-hybrid
```

### 기존 파일은 유지됨

fullstack/ 디렉토리의 기존 파일들은 호환성을 위해 유지되지만, 통합 오케스트레이터 사용을 권장합니다.

---

## 문제 해결

### MCP 연결 실패

```bash
# Figma MCP 서버 재시작
# Claude Code 설정에서 MCP 서버 상태 확인
```

### 빌드 실패

```bash
flutter clean
flutter pub get
flutter analyze
```

### 정확도 미달

- L3/L4 수정은 수동 승인 필요
- 복잡한 레이아웃은 Ralph Pure 전략 권장

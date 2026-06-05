# UI Design Agent 사용 가이드

프로덕션 수준의 프론트엔드 UI/UX를 설계, 구현, 리뷰할 때는 `design-harness`를 1차 진입점으로 사용합니다. 오래된 `/fd-*` 단계형 스킬과 12개 aesthetic template 방식은 더 이상 활성 라우팅 기준이 아닙니다.

## 기본 요청

```text
"랜딩페이지 디자인해줘"
"대시보드 UX 리뷰해줘"
"이 화면 AI스럽지 않게 리디자인해줘"
"모바일에서 깨지는 UI 하드닝해줘"
"컬러/타이포그래피를 제품에 맞게 정리해줘"
```

## Design Harness Modes

| 모드 | 용도 |
|---|---|
| `shape` | 코드 전 UX/UI 방향, 정보구조, 화면 구성 결정 |
| `craft` | 새 UI surface를 구현까지 진행 |
| `audit` | UX, 접근성, 반응형, visual QA 리뷰 |
| `polish` | 기존 화면을 출시 전 품질로 다듬기 |
| `redesign` | 기존 IA/기능을 보존하면서 현대화 |
| `typeset` | 타이포그래피, 위계, 폰트 체계 정리 |
| `colorize` | 팔레트, 테마, 토큰 방향 정리 |
| `animate` | 목적 있는 모션/마이크로인터랙션 설계 |
| `harden` | 상태, overflow, 모바일, i18n, reduced-motion 보강 |

## 처리 흐름

1. 제품/브랜드/사용자 맥락을 읽고 대표 UI 파일을 확인합니다.
2. 한 줄 design read를 작성합니다.
3. `DISTINCTION`, `MOTION`, `DENSITY` 세 다이얼을 정합니다.
4. Product register 또는 Brand register를 선택합니다.
5. 필요하면 `ui-styling`, `design-system`, `logo-creator`, `banner-design`로 위임합니다.
6. 구현 후 slop detector와 브라우저 검증을 수행합니다.

## 다이얼 기준

| 화면 유형 | DISTINCTION | MOTION | DENSITY |
|---|---:|---:|---:|
| SaaS/운영 대시보드 | 3-5 | 2-4 | 6-9 |
| 개발자 도구/API 콘솔 | 3-6 | 1-3 | 6-9 |
| 브랜드/캠페인/포트폴리오 | 6-9 | 4-8 | 2-5 |
| 공공/규제/법무/재무 | 2-4 | 1-3 | 5-8 |

## 하위 스킬 경계

| 작업 | 사용 스킬 |
|---|---|
| UI 방향, 리디자인, UX 리뷰, anti-slop | `design-harness` |
| Tailwind/shadcn 컴포넌트 구현 | `ui-styling` |
| 토큰, CSS 변수, 디자인 시스템 구조 | `design-system` |
| 로고, 브랜드 마크, favicon, app icon | `logo-creator` |
| 배너, 커버, 광고 크리에이티브 | `banner-design` |

## 검증 명령

UI 코드가 있는 프로젝트에서는 변경한 UI 디렉터리를 대상으로 실행합니다.

```bash
node .claude/skills/design-harness/scripts/detect-design-slop.mjs src app components pages
```

프론트엔드 앱을 실제로 실행할 수 있으면 브라우저에서 desktop/mobile viewport를 확인합니다.

## Legacy

다음 항목은 더 이상 1차 디자인 지침으로 사용하지 않습니다.

| Legacy | 대체 |
|---|---|
| `/fd-context`, `/fd-inspiration`, `/fd-direction` | `design-harness shape` |
| `/fd-typography`, `/fd-color`, `/fd-spacing` | `design-harness typeset/colorize` + `design-system` |
| `/fd-motion`, `/fd-effects`, `/fd-interactions` | `design-harness animate/polish` |
| `/fd-landing`, `/fd-dashboard`, `/fd-mobile` | `design-harness craft/redesign/harden` |
| `/fd-a11y`, `/fd-responsive`, `/fd-perf` | `design-harness audit/harden` + framework performance skill |

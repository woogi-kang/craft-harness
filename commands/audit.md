---
name: audit
description: AI 에이전트 하니스 설정 종합 감사 (0-100 스코어카드)
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

현재 Craft Harness 설정을 종합 감사하고 스코어카드를 생성합니다.

## 감사 항목 (10개 카테고리, 각 10점)

### 1. Adapter guidance 품질 (10점)
- 프로젝트 구조 설명 존재
- 도메인 에이전트 테이블 존재
- docs 참조 존재
- 간결성

### 2. 에이전트 정의 (10점)
- `agents/` 에 에이전트 존재
- 각 에이전트에 frontmatter (name, description, model)
- 카테고리별 분류
- tools 명시

### 3. 스킬 품질 (10점)
- YAML frontmatter 100% 존재
- description 필드 채워짐
- metadata.version 존재
- references/ 참조 무결성

### 4. 커맨드 완성도 (10점)
- allowed-tools 명시
- 절차 문서화
- 사용 예시 포함

### 5. Hook 설정 (10점)
- PostToolUse hooks 등록
- Hook 스크립트 실행 가능 (chmod +x)
- 에러 시 non-blocking (exit 0)

### 6. Rules 체계 (10점)
- 공개 repo guidance와 docs 구조 존재
- 언어별 rules 존재
- README와 adapter 문서에서 참조

### 7. 멀티환경 동기화 (10점)
- `craft install --target openhands`가 `.agents/skills/` export 가능
- `craft install --target gemini`가 `GEMINI.md` 생성 가능
- `craft install --target codex`와 `opencode`가 `AGENTS.md` 생성 가능

### 8. 설정 최적화 (10점)
- env.MAX_THINKING_TOKENS 설정
- runtime별 설정 guidance 존재
- statusLine 설정

### 9. 문서화 (10점)
- docs/CONTRIBUTING.md 존재
- CHANGELOG.md 존재
- 스킬 카탈로그 존재

### 10. 자동화 (10점)
- 검증 스크립트 존재 (validate-skills.sh)
- 카탈로그 생성 스크립트 존재
- 무결성 검사 스크립트 존재

## 출력 형식
```
=== Craft Harness Audit ===

Category                    Score   Notes
Adapter guidance 품질       9/10    ✅ 간결, docs 참조
에이전트 정의               8/10    ⚠️ 2개 에이전트 frontmatter 누락
스킬 품질                   10/10   ✅ 313/313 frontmatter
커맨드 완성도               9/10    ✅
Hook 설정                   10/10   ✅ usage-tracker + quality-gate
Rules 체계                  10/10   ✅ common + python + typescript
멀티환경 동기화             10/10   ✅ install target 검증
설정 최적화                 10/10   ✅ 토큰 + 컴팩션 설정
문서화                      10/10   ✅ CONTRIBUTING + CHANGELOG + catalog
자동화                      10/10   ✅ validate + catalog + integrity

=== Total: 96/100 ===

권장 조치:
1. 에이전트 frontmatter 보완 (2개)
```

## 사용 예시
```
/audit
```

---
name: skill-audit
description: 스킬 품질 감사 — Keep/Improve/Retire/Merge 판정
allowed-tools: ["Bash", "Read", "Glob", "Grep", "AskUserQuestion"]
---

$ARGUMENTS

설치된 스킬의 품질을 감사하고 조치를 판정합니다.

## 절차

### 1. 인벤토리
- `.claude/skills/` 전체 스캔
- 각 스킬의 SKILL.md 읽기
- frontmatter 메타데이터 추출 (name, description, version, category)

### 2. 평가 기준
각 스킬을 다음 기준으로 평가:
- **콘텐츠 충실도**: SKILL.md가 실질적 내용을 포함하는지 (템플릿만 있으면 감점)
- **중복**: 다른 스킬과 기능이 겹치는지
- **참조 무결성**: references/ 파일이 실제로 존재하는지
- **최신성**: 기술 스택 버전이 현재와 맞는지
- **사용 빈도**: `.claude/logs/usage.jsonl` 에서 호출 기록 확인

### 3. 판정
각 스킬에 대해 하나를 선택:
| 판정 | 의미 |
|------|------|
| **Keep** | 현재 상태 유지 |
| **Improve** | 내용 보강 필요 (구체적 제안 포함) |
| **Update** | 기술 버전 업데이트 필요 |
| **Retire** | 더 이상 사용하지 않음 → 삭제 후보 |
| **Merge** | 다른 스킬에 통합 가능 |

### 4. 보고
```
=== Skill Audit Report ===
Total: {N} skills scanned

Verdict     Count
Keep        {n}
Improve     {n}
Update      {n}
Retire      {n}
Merge       {n}

--- Improve ---
skill-name: {구체적 개선 제안}

--- Retire ---
skill-name: {이유}

--- Merge ---
skill-a → skill-b: {이유}
```

### 5. 실행
Retire/Merge 판정은 사용자 확인 후에만 실행.

## 스코프
- `$ARGUMENTS` 없으면 전체 스캔
- 카테고리 지정 가능: `/skill-audit 💻 개발`
- 특정 스킬: `/skill-audit fastapi-agent-skills`

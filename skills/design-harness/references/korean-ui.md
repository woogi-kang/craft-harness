# Korean UI Layer

Apply when `lang="ko"`, Korean copy is present, or the user is Korean.

## Typography

- Prefer `Pretendard`, `SUIT`, or an existing Korean brand font for Korean UI.
- Avoid Korean text in `leading-none`; use `leading-tight` to `leading-relaxed`.
- Use `word-break: keep-all` for headings and important Korean phrases.
- Use `text-wrap: balance` for headings where supported.
- Body copy should stay readable at mobile widths; do not over-tighten tracking.
- Keep numeric data aligned with `font-variant-numeric: tabular-nums`.

## Copy

- Keep one honorific register: `합니다/하세요` or a deliberately chosen alternative.
- Avoid translationese and buzzwords:
  - 혁신적인, 획기적인, 차세대, 원활한, 게임 체인저, 솔루션 as a standalone noun.
- CTA labels should be concrete:
  - `무료로 시작하기`
  - `3분 만에 만들어보기`
  - `지금 바로 체험하기`
  - `상담 예약하기`

## Mobile

- Korean web traffic is often mobile-heavy. Design mobile first unless project data says otherwise.
- Use `min-h-[100dvh]`, not `h-screen`.
- Primary CTAs should be at least 48px tall on mobile.
- Keep fixed bars clear of safe areas and browser chrome.
- Test long Korean headings at 360-390px width.

## Korean Anti-Patterns

- Korean text broken between syllables in headings.
- English font chosen for Korean body fallback by accident.
- Literal English slogan structure translated into awkward Korean.
- Purple/blue AI gradients as default.
- Generic Korean names like `김철수` and `이영희`; use realistic names when mock data is needed.

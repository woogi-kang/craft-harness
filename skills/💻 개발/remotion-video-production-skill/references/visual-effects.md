# Visual Effects and Data-driven Scenes

## 텍스트 애니메이션

권장 패턴:

- typewriter: 문자열 `slice()`
- word highlight: 하이라이트 배경을 scaleX로 전개
- per-character opacity 애니메이션은 과하게 복잡하면 피한다

## 차트

지원하기 좋은 장면:

- bar chart
- pie chart
- line chart
- stock chart

원칙:

- 서드파티 차트 라이브러리의 내장 애니메이션은 끈다.
- 데이터 드로잉은 `useCurrentFrame()` 기반으로만 제어한다.

## Lottie

- 외부 Lottie JSON을 fetch해서 `delayRender()` 뒤에 렌더한다.
- 장식용 모션이나 로고 reveal에 적합하다.

## Light Leak

- 전환 지점 위에 얹는 overlay 효과다.
- `TransitionSeries.Overlay`와 궁합이 좋다.

## Audio Visualization

가능한 패턴:

- spectrum bars
- waveform
- bass-reactive scale/opacity

주의:

- child component가 Sequence 안에 있더라도 오디오 시각화용 `frame`은 부모 기준으로 내려준다.

## 텍스트/DOM 측정

- 긴 이름, 문구, 자막이 박스를 넘칠 수 있으면 측정 helper를 쓴다.
- 폰트 로딩 완료 전 측정은 피한다.


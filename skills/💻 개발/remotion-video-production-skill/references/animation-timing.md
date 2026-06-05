# Animation and Timing

## 기본 규칙

- 모든 애니메이션은 `useCurrentFrame()` 기준이다.
- 초 단위 설계를 하더라도 코드에서는 `fps`를 곱해 프레임으로 변환한다.
- CSS transition과 CSS animation은 사용하지 않는다.

## 기본 보간

```tsx
import { interpolate, useCurrentFrame } from "remotion";

const frame = useCurrentFrame();
const opacity = interpolate(frame, [0, 30], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```

## spring

```tsx
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const progress = spring({
  frame,
  fps,
  config: { damping: 200 },
});
```

권장 감각:

- `damping: 200`: 차분하고 반동이 거의 없음
- `damping: 20, stiffness: 200`: 빠르고 스냅한 UI 느낌
- `damping: 8`: 바운스가 큰 장난스러운 모션

## Sequence

타임라인에서 특정 컴포넌트가 언제 등장하는지 제어한다.

```tsx
import { Sequence } from "remotion";

<Sequence from={30} durationInFrames={90} premountFor={30}>
  <Title />
</Sequence>;
```

중요:

- `premountFor`를 습관적으로 넣어 초기 로딩 깜빡임을 줄인다.
- `Sequence` 내부의 `useCurrentFrame()`은 로컬 프레임으로 바뀐다.

## Series

장면이 연속 재생될 때 쓴다.

```tsx
import { Series } from "remotion";

<Series>
  <Series.Sequence durationInFrames={60}>
    <Intro />
  </Series.Sequence>
  <Series.Sequence durationInFrames={90}>
    <Main />
  </Series.Sequence>
</Series>;
```

## 트리밍

애니메이션 시작 부분을 잘라낼 때는 `from`에 음수를 줄 수 있다.

```tsx
<Sequence from={-15}>
  <MyAnimation />
</Sequence>
```

종료 시점 잘라내기는 `durationInFrames`로 처리한다.

## TransitionSeries

장면 전환 전용 시퀀스다.

적합한 케이스:

- 웨딩 하이라이트 씬 전환
- 프레젠테이션 스타일 컷 전환
- light leak overlay

핵심 포인트:

- transition은 앞뒤 씬이 겹치므로 전체 길이가 줄어든다.
- overlay는 전체 길이를 줄이지 않는다.


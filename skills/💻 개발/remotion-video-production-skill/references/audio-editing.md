# Audio Editing in Remotion

오디오 편집은 `@remotion/media`의 `<Audio>`와 `Sequence` 조합으로 해결한다.

## 가능한 것

- 특정 구간만 재생
- 페이드 인 / 페이드 아웃
- 중간 구간 스킵
- 여러 구간을 이어붙이기
- 두 구간 겹치기와 크로스페이드
- 볼륨 자동화
- 속도 변경, 루프, 피치 조정

## 불가능하거나 별도 도구가 필요한 것

- 단일 혼합본 1개에서 보컬만 제거해 MR 만들기
- 정교한 stem 분리
- 음정 보정, 노이즈 복원 같은 DAW 수준 복원 작업

위 작업은 Demucs, UVR, DAW 같은 별도 도구가 필요하다.

## 설치

```bash
npx remotion add @remotion/media
```

## 기본 패턴

```tsx
import { Audio } from "@remotion/media";
import { staticFile } from "remotion";

export const Music = () => {
  return <Audio src={staticFile("wedding-song.mp3")} />;
};
```

## 트리밍

`trimBefore`와 `trimAfter`는 프레임 단위로 준다.

```tsx
import { Audio } from "@remotion/media";
import { staticFile, useVideoConfig } from "remotion";

export const IntroOnly = () => {
  const { fps } = useVideoConfig();

  return (
    <Audio
      src={staticFile("wedding-song.mp3")}
      trimBefore={0}
      trimAfter={18 * fps}
    />
  );
};
```

## 시작 시점 지연

```tsx
import { Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";

<Sequence from={30}>
  <Audio src={staticFile("wedding-song.mp3")} />
</Sequence>;
```

## 페이드 인 / 페이드 아웃

볼륨 콜백의 `f`는 "오디오가 시작된 뒤의 로컬 프레임"이다.

```tsx
import { interpolate, staticFile, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";

export const FadedMusic = () => {
  const { fps } = useVideoConfig();

  return (
    <Audio
      src={staticFile("wedding-song.mp3")}
      volume={(f) => {
        if (f < 2 * fps) {
          return interpolate(f, [0, 2 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
        }

        const outroStart = 30 * fps;
        return interpolate(f, [outroStart, outroStart + 4 * fps], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
      }}
    />
  );
};
```

## 구간을 이어붙여 재편집하기

하나의 원본에서 필요한 구간만 골라 새 타임라인으로 재구성할 수 있다.

```tsx
import { Sequence, staticFile, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";

export const WeddingEntranceEdit = () => {
  const { fps } = useVideoConfig();

  return (
    <>
      <Sequence from={0} durationInFrames={18 * fps}>
        <Audio src={staticFile("wedding-song.mp3")} trimAfter={18 * fps} />
      </Sequence>

      <Sequence from={18 * fps} durationInFrames={24 * fps}>
        <Audio
          src={staticFile("wedding-song.mp3")}
          trimBefore={42 * fps}
          trimAfter={66 * fps}
        />
      </Sequence>
    </>
  );
};
```

위 예시는 `18초` 뒤에 원본의 `42초` 지점부터 이어붙인다. 즉, `18초-42초` 구간이 스킵된다.

## 크로스페이드

두 구간을 몇 초 겹쳐 배치한 뒤 한쪽 볼륨은 내려가고 다른 쪽은 올라가게 만든다.

```tsx
import { Sequence, interpolate, staticFile, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";

export const CrossfadeEdit = () => {
  const { fps } = useVideoConfig();
  const overlap = 2 * fps;

  return (
    <>
      <Sequence from={0} durationInFrames={20 * fps}>
        <Audio
          src={staticFile("song-a.mp3")}
          volume={(f) =>
            interpolate(f, [18 * fps, 20 * fps], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      </Sequence>

      <Sequence from={20 * fps - overlap} durationInFrames={24 * fps}>
        <Audio
          src={staticFile("song-b.mp3")}
          volume={(f) =>
            interpolate(f, [0, overlap], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      </Sequence>
    </>
  );
};
```

## stem 파일이 있을 때 MR만 재생

보컬과 반주가 분리된 경우에만 이런 편집을 한다.

```tsx
<>
  <Sequence from={0} durationInFrames={20 * fps}>
    <Audio src={staticFile("full-mix.mp3")} />
  </Sequence>

  <Sequence from={20 * fps} durationInFrames={16 * fps}>
    <Audio src={staticFile("instrumental.mp3")} />
  </Sequence>

  <Sequence from={36 * fps} durationInFrames={24 * fps}>
    <Audio src={staticFile("full-mix.mp3")} />
  </Sequence>
</>;
```

## FFmpeg를 함께 쓸 때

최종 오디오 파일만 빨리 뽑아야 하거나, 비파괴 타임라인이 아니라 실제 파일 컷이 필요하면 FFmpeg도 쓴다.

```bash
bunx remotion ffmpeg -i public/input.mp3 -ss 00:00:18 -to 00:00:42 public/highlight.mp3
```

Remotion은 "타임라인 설계", FFmpeg는 "실제 파일 절단"에 강하다.


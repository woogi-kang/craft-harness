# Media Assets and Dynamic Metadata

## 자산 위치 규칙

- 로컬 자산은 `public/` 폴더에 둔다.
- 코드에서는 항상 `staticFile()`로 참조한다.
- 원격 URL도 가능하지만 렌더 안정성과 재현성을 생각하면 로컬 보관이 낫다.

```tsx
import { Img, staticFile } from "remotion";
import { Video, Audio } from "@remotion/media";

<Img src={staticFile("cover.png")} />;
<Video src={staticFile("clip.mp4")} />;
<Audio src={staticFile("bgm.mp3")} />;
```

## 이미지 규칙

- 기본 HTML `<img>` 대신 Remotion의 `<Img>`를 쓴다.
- animated GIF/APNG/WebP는 `AnimatedImage` 또는 `@remotion/gif`를 고려한다.

## 폰트 규칙

- Google Font: `@remotion/google-fonts`
- 로컬 폰트: `@remotion/fonts`
- 텍스트 측정 전에는 폰트 로딩이 끝나 있어야 한다.

## Composition 기본 정의

```tsx
import { Composition } from "remotion";
import { MyComp } from "./MyComp";

<Composition
  id="MyComp"
  component={MyComp}
  durationInFrames={300}
  fps={30}
  width={1920}
  height={1080}
/>;
```

## 동적 길이와 해상도

소스 길이/해상도에 따라 composition이 달라지면 `calculateMetadata`를 쓴다.

```tsx
import { Composition, CalculateMetadataFunction, staticFile } from "remotion";
import { getAudioDuration } from "./get-audio-duration";

type Props = {
  musicFile: string;
};

const calculateMetadata: CalculateMetadataFunction<Props> = async ({ props }) => {
  const durationInSeconds = await getAudioDuration(staticFile(props.musicFile));

  return {
    durationInFrames: Math.ceil(durationInSeconds * 30),
    defaultOutName: props.musicFile.replace(/\.[^.]+$/, ""),
  };
};
```

## useful helper patterns

- 오디오 길이 읽기: Mediabunny 기반 duration helper
- 영상 길이 읽기: video duration helper
- 영상 해상도 읽기: dimensions helper
- 디코딩 가능 여부 검사: `canDecode()` 스타일 helper
- 특정 시점 썸네일 생성: frame extraction helper

이런 helper는 project에 함께 두면 재사용성이 높다.

## 매개변수화

템플릿성 작업이면 Zod schema를 붙여 파라미터 편집 가능하게 만든다.

적합한 케이스:

- 곡 파일명, 제목, 신랑/신부 이름
- 씬별 이미지 목록
- 캡션 JSON 파일명
- 색상/폰트 테마


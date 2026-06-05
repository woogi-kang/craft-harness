# Advanced Scenes and Export

## 3D

- `@remotion/three`의 `ThreeCanvas`를 사용한다.
- `useFrame()` 기반 자동 애니메이션은 금지하고 `useCurrentFrame()`으로만 구동한다.
- 조명은 명시적으로 둔다.

## 지도 애니메이션

- Mapbox를 사용한다.
- 기본 인터랙션, fade 같은 자체 애니메이션은 꺼둔다.
- 맵 로딩은 `useDelayRender()`로 감싼다.

적합한 케이스:

- 웨딩 식장까지의 여정 소개
- 여행/동선 하이라이트
- 행사 위치 안내 영상

## 투명 비디오

두 가지 주력 출력:

- 편집툴용: ProRes 4444
- 웹용: VP9 WebM with alpha

## FFmpeg / FFprobe

Remotion 쪽 래퍼를 통해 호출할 수 있다.

```bash
bunx remotion ffmpeg -i input.mp4 output.mp3
bunx remotion ffprobe input.mp4
```

## 언제 FFmpeg를 같이 쓰나

- 실제 파일을 자르고 싶을 때
- 영상/오디오 포맷 변환이 필요할 때
- 사전 추출물 생성이 필요할 때

## 렌더링 판단 기준

- 최종본이 브라우저 재생용이면 H.264 또는 VP9
- 편집툴 왕복이면 ProRes
- 알파가 필요하면 이미지 포맷과 픽셀 포맷까지 함께 맞춘다


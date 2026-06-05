# Captions and Subtitles

## 표준 포맷

자막은 `@remotion/captions`의 `Caption[]` JSON 포맷으로 다루는 것을 기본으로 한다.

```ts
type Caption = {
  text: string;
  startMs: number;
  endMs: number;
  timestampMs: number | null;
  confidence: number | null;
};
```

## 자막 소스

- 음성을 직접 전사: Whisper.cpp 기반 전사 후 JSON 생성
- 기존 자막 있음: `.srt`를 파싱해 JSON으로 변환

## 표시 패턴

- 문장 단위 페이지 전환
- TikTok 스타일 여러 단어 묶음
- 현재 발화 단어 하이라이트

## 구현 메모

- 자막 파일을 fetch할 때는 `useDelayRender()`로 렌더를 지연한다.
- 자막은 whitespace-sensitive 하므로 `whiteSpace: "pre"` 처리를 신경 쓴다.
- 자막 렌더링 로직은 별도 컴포넌트 파일로 분리한다.

## 사용 시나리오

- 결혼식 오프닝 영상 자막
- 인터뷰/브이로그형 릴스 자막
- 보이스오버 기반 설명 영상

## 보이스오버와 함께 쓸 때

- 씬별 TTS 파일 생성
- 각 파일 길이 합으로 `calculateMetadata`에서 전체 길이 계산
- 자막 JSON도 씬별 파일로 쪼개면 관리가 쉽다


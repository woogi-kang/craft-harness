# Next.js 16 + Zustand 5 Update Reference

Last verified: 2026-05-25

## Version Baseline

| 영역 | 기준 |
|------|------|
| Next.js | 16.2.x |
| React / React DOM | 19.2.x |
| Node.js | 20.19+ 권장 |
| TypeScript | 5.9+ 권장 |
| Zustand | 5.0.x |
| TanStack Query | 5.x |
| Zod | 4.x |
| Vitest / Playwright | 4.x / 1.60+ |

## Next.js 16 Migration Checklist

- `next dev --turbopack`를 제거하고 `next dev`를 기본으로 사용한다. Turbopack은 기본값이다.
- `next lint`를 제거하고 `eslint . --max-warnings=0`처럼 ESLint CLI를 직접 사용한다.
- `middleware.ts`를 `proxy.ts`로 이전한다. Proxy 파일은 default export 또는 named `proxy` 함수 하나만 export한다.
- Proxy는 Node.js Runtime이 기본값이며 `runtime` config를 사용할 수 없다.
- `cookies()`, `headers()`, `draftMode()`, `params`, `searchParams`는 비동기 API로 다룬다.
- `typedRoutes`는 top-level config로 사용한다. `experimental.typedRoutes`를 쓰지 않는다.
- Cache Components 신규 코드는 `cacheComponents: true`, `"use cache"`, `cacheTag`, `cacheLife`를 우선 검토한다.
- `revalidateTag`는 profile 인자가 필요하다. stale-while-revalidate는 `revalidateTag(tag, 'max')`, Server Action 즉시 갱신은 `updateTag(tag)`를 사용한다.
- `serverComponentsExternalPackages` 대신 `serverExternalPackages`를 사용한다.
- `serverRuntimeConfig`/`publicRuntimeConfig`에 의존하지 않는다. 환경 변수 또는 명시적 서버 설정으로 대체한다.

## Zustand 5 Checklist

- 서버 상태는 Zustand에 저장하지 않는다. RSC fetch, Server Action, TanStack Query 캐시를 사용한다.
- URL로 공유되어야 하는 상태는 nuqs에 둔다.
- Zustand는 모달, drawer, selected id, 임시 wizard state, 사용자 preference 같은 클라이언트 UI 상태에 한정한다.
- React Server Components에서 Zustand hook/context를 읽거나 쓰지 않는다.
- 요청별 초기값이 필요한 store는 `createStore` factory + Client Provider로 생성한다.
- 객체/배열 selector는 `useShallow(selector)`로 안정적인 참조를 반환한다.
- v4 스타일 `useStore(selector, shallow)`가 필요하면 `createWithEqualityFn`을 `zustand/traditional`에서 가져오고 `use-sync-external-store`를 설치한다.
- `setState(nextState, true)`는 전체 state를 전달한다.
- `persist`는 `partialize`, `version`, `migrate`를 함께 설계하고 민감 정보는 저장하지 않는다.

## Primary Sources

- https://nextjs.org/blog/next-16
- https://nextjs.org/blog/next-16-2
- https://nextjs.org/docs/app/guides/upgrading/version-16
- https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- https://react.dev/blog/2025/10/01/react-19-2
- https://github.com/pmndrs/zustand/blob/main/docs/reference/migrations/migrating-to-v5.md
- https://github.com/pmndrs/zustand/blob/main/docs/learn/guides/nextjs.md

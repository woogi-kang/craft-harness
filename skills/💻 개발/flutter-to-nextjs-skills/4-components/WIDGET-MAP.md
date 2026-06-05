# Flutter Widget → React Component 매핑 레퍼런스

빠른 참조를 위한 위젯 매핑 가이드입니다.

---

## 기본 위젯

| Flutter | React/Next.js | Tailwind |
|---------|---------------|----------|
| `Container` | `<div>` | 스타일 적용 |
| `SizedBox(width: 8)` | `<div>` | `w-2` |
| `SizedBox(height: 16)` | `<div>` | `h-4` |
| `Padding` | `<div>` | `p-*` |
| `Center` | `<div>` | `flex items-center justify-center` |
| `Align` | `<div>` | `flex` + alignment |

---

## 레이아웃

| Flutter | React/Next.js | Tailwind |
|---------|---------------|----------|
| `Column` | `<div>` | `flex flex-col` |
| `Row` | `<div>` | `flex flex-row` |
| `Wrap` | `<div>` | `flex flex-wrap` |
| `Stack` | `<div>` | `relative` |
| `Positioned` | `<div>` | `absolute` + position |
| `Expanded` | child | `flex-1` |
| `Flexible` | child | `flex-1` or `flex-auto` |
| `Spacer` | `<div>` | `flex-1` |

### MainAxisAlignment

| Flutter | Tailwind |
|---------|----------|
| `start` | `justify-start` |
| `end` | `justify-end` |
| `center` | `justify-center` |
| `spaceBetween` | `justify-between` |
| `spaceAround` | `justify-around` |
| `spaceEvenly` | `justify-evenly` |

### CrossAxisAlignment

| Flutter | Tailwind |
|---------|----------|
| `start` | `items-start` |
| `end` | `items-end` |
| `center` | `items-center` |
| `stretch` | `items-stretch` |

---

## 스크롤

| Flutter | React/Next.js | 비고 |
|---------|---------------|------|
| `SingleChildScrollView` | `<div>` | `overflow-auto` |
| `ListView` | `map()` | 기본 |
| `ListView.builder` | `map()` + virtualization | `@tanstack/react-virtual` |
| `GridView` | `<div>` | `grid grid-cols-*` |
| `CustomScrollView` | 커스텀 | Framer Motion |
| `RefreshIndicator` | 라이브러리 | `react-pull-to-refresh` |

---

## 텍스트

| Flutter | React/Next.js | Tailwind |
|---------|---------------|----------|
| `Text` | `<span>` or `<p>` | typography |
| `RichText` | JSX 조합 | |
| `SelectableText` | `<p>` | `select-text` |

### TextStyle → Tailwind

| Flutter | Tailwind |
|---------|----------|
| `fontSize: 10` | `text-[10px]` |
| `fontSize: 12` | `text-xs` |
| `fontSize: 14` | `text-sm` |
| `fontSize: 16` | `text-base` |
| `fontSize: 18` | `text-lg` |
| `fontSize: 20` | `text-xl` |
| `fontSize: 24` | `text-2xl` |
| `fontWeight: FontWeight.w300` | `font-light` |
| `fontWeight: FontWeight.w400` | `font-normal` |
| `fontWeight: FontWeight.w500` | `font-medium` |
| `fontWeight: FontWeight.w600` | `font-semibold` |
| `fontWeight: FontWeight.w700` | `font-bold` |
| `fontStyle: FontStyle.italic` | `italic` |
| `decoration: TextDecoration.underline` | `underline` |
| `decoration: TextDecoration.lineThrough` | `line-through` |

---

## 버튼

| Flutter | shadcn/ui | Variant |
|---------|-----------|---------|
| `ElevatedButton` | `Button` | `default` |
| `TextButton` | `Button` | `ghost` |
| `OutlinedButton` | `Button` | `outline` |
| `IconButton` | `Button` | `size="icon"` |
| `FloatingActionButton` | `Button` | `size="icon"` + fixed position |

---

## 입력

| Flutter | shadcn/ui | 비고 |
|---------|-----------|------|
| `TextField` | `Input` | |
| `TextFormField` | `Input` | + react-hook-form |
| `Checkbox` | `Checkbox` | |
| `Switch` | `Switch` | |
| `Radio` | `RadioGroup` | |
| `Slider` | `Slider` | |
| `DropdownButton` | `Select` | |
| `DatePicker` | `Calendar` + `Popover` | |
| `TimePicker` | 커스텀 | |

---

## 다이얼로그/시트

| Flutter | shadcn/ui |
|---------|-----------|
| `AlertDialog` | `AlertDialog` |
| `SimpleDialog` | `Dialog` |
| `BottomSheet` | `Sheet side="bottom"` |
| `showModalBottomSheet` | `Sheet` |
| `Snackbar` | `toast` (sonner) |

---

## 네비게이션

| Flutter | Next.js |
|---------|---------|
| `AppBar` | 커스텀 Header |
| `Drawer` | `Sheet side="left"` |
| `BottomNavigationBar` | 커스텀 BottomNav |
| `TabBar` | `Tabs` |
| `PageView` | 커스텀 또는 swiper |
| `NavigationRail` | 커스텀 Sidebar |

---

## 이미지/아이콘

| Flutter | Next.js |
|---------|---------|
| `Image.network` | `next/image` |
| `Image.asset` | `next/image` (public/) |
| `Icon` | `lucide-react` |
| `SvgPicture` | React SVG 또는 `next/image` |
| `CircleAvatar` | `Avatar` (shadcn) |

---

## 카드/리스트

| Flutter | shadcn/ui |
|---------|-----------|
| `Card` | `Card` |
| `ListTile` | 커스텀 (flex 기반) |
| `ExpansionTile` | `Accordion` |
| `Divider` | `Separator` |

---

## 진행/로딩

| Flutter | React | 비고 |
|---------|-------|------|
| `CircularProgressIndicator` | `Loader2` | lucide + animate-spin |
| `LinearProgressIndicator` | `Progress` | shadcn |
| `Shimmer` | `Skeleton` | shadcn |

---

## 제스처

| Flutter | React |
|---------|-------|
| `GestureDetector.onTap` | `onClick` |
| `GestureDetector.onDoubleTap` | `onDoubleClick` |
| `GestureDetector.onLongPress` | `onContextMenu` or 커스텀 |
| `InkWell` | `onClick` + hover 스타일 |
| `Draggable` | `@dnd-kit/core` |
| `Dismissible` | `framer-motion` drag |

---

## 애니메이션

| Flutter | React |
|---------|-------|
| `AnimatedContainer` | `motion.div` (framer-motion) |
| `AnimatedOpacity` | `motion.div` animate opacity |
| `FadeTransition` | `AnimatePresence` + opacity |
| `SlideTransition` | `motion.div` animate x/y |
| `ScaleTransition` | `motion.div` animate scale |
| `Hero` | `layoutId` (framer-motion) |

---

## 폼/검증

| Flutter | React |
|---------|-------|
| `Form` | `<form>` + react-hook-form |
| `GlobalKey<FormState>` | `useForm()` |
| `TextEditingController` | `register()` or `ref` |
| `validator` | `zod` schema |
| `autovalidateMode` | `mode: 'onChange'` |

---

## 상태 관련

| Flutter | React |
|---------|-------|
| `setState` | `useState` |
| `initState` | `useEffect(() => {}, [])` |
| `dispose` | `useEffect` cleanup |
| `didChangeDependencies` | `useEffect` with deps |
| `didUpdateWidget` | `useEffect` with props |

---

## Provider/Context

| Flutter | React |
|---------|-------|
| `Provider.of<T>(context)` | `useContext` or Zustand |
| `Consumer<T>` | Hook 사용 |
| `context.read<T>()` | `useStore.getState()` |
| `context.watch<T>()` | `useStore()` |

---

## 기타

| Flutter | React/Next.js |
|---------|---------------|
| `FutureBuilder` | `useQuery` or `use()` |
| `StreamBuilder` | `useQuery` + WebSocket |
| `ValueListenableBuilder` | `useSyncExternalStore` |
| `MediaQuery` | `useMediaQuery` hook |
| `Theme.of(context)` | Tailwind CSS 변수 |
| `Navigator` | `useRouter` |
| `WillPopScope` | `beforeunload` event |

# Component Pattern Reference

shadcn/ui + Atomic Design 컴포넌트 패턴 및 샘플 코드 레퍼런스입니다.

## Atomic Design 계층

```
┌─────────────────────────────────────────────────────────────────┐
│                         PAGES                                    │
│    app/page.tsx - 실제 라우트 페이지                             │
├─────────────────────────────────────────────────────────────────┤
│                       TEMPLATES                                  │
│    DashboardLayout, AuthLayout - 페이지 레이아웃 뼈대            │
├─────────────────────────────────────────────────────────────────┤
│                       ORGANISMS                                  │
│    Header, Sidebar, DataTable - 복잡한 UI 섹션                   │
├─────────────────────────────────────────────────────────────────┤
│                       MOLECULES                                  │
│    SearchBar, FormField, UserAvatar - 단일 기능 조합             │
├─────────────────────────────────────────────────────────────────┤
│                         ATOMS                                    │
│    Button, Input, Card - shadcn/ui 기본 컴포넌트                 │
├─────────────────────────────────────────────────────────────────┤
│                        TOKENS                                    │
│    CSS Variables - colors, spacing, typography                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 디렉토리 구조

```
src/components/
├── ui/                    # shadcn/ui 컴포넌트 (자동 생성)
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   └── ...
│
├── atoms/                 # 커스텀 Atoms
│   ├── logo.tsx
│   ├── loading-spinner.tsx
│   └── badge-status.tsx
│
├── molecules/             # Molecules
│   ├── search-bar.tsx
│   ├── form-field.tsx
│   ├── user-avatar.tsx
│   └── nav-link.tsx
│
├── organisms/             # Organisms
│   ├── header.tsx
│   ├── sidebar.tsx
│   ├── data-table/
│   │   ├── data-table.tsx
│   │   ├── columns.tsx
│   │   └── toolbar.tsx
│   └── forms/
│       ├── login-form.tsx
│       └── register-form.tsx
│
└── templates/             # Templates
    ├── dashboard-layout.tsx
    ├── auth-layout.tsx
    └── marketing-layout.tsx
```

---

## Tokens (CSS Variables)

### globals.css

```css
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

:root {
  /* Colors */
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --destructive-foreground: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);

  /* Custom Colors */
  --success: oklch(0.76 0.18 145);
  --success-foreground: oklch(0.20 0.05 145);
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
  --info: oklch(0.70 0.15 250);
  --info-foreground: oklch(0.20 0.05 250);

  /* Radius */
  --radius: 0.625rem;

  /* Spacing */
  --sidebar-width: 280px;
  --header-height: 64px;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.145 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.145 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.396 0.141 25.723);
  --destructive-foreground: oklch(0.637 0.237 25.331);
  --border: oklch(0.269 0 0);
  --input: oklch(0.269 0 0);
  --ring: oklch(0.439 0 0);

  /* Custom Colors - Dark */
  --success: oklch(0.45 0.12 145);
  --success-foreground: oklch(0.95 0.03 145);
  --warning: oklch(0.41 0.11 46);
  --warning-foreground: oklch(0.99 0.02 95);
  --info: oklch(0.45 0.12 250);
  --info-foreground: oklch(0.95 0.03 250);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-success: var(--success);
  --color-success-foreground: var(--success-foreground);
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
  --color-info: var(--info);
  --color-info-foreground: var(--info-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}
```

---

## Atoms (기본 컴포넌트)

### Loading Spinner

```tsx
// components/atoms/loading-spinner.tsx
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
};

export function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  return (
    <Loader2 className={cn('animate-spin', sizeClasses[size], className)} />
  );
}
```

### Badge Status

```tsx
// components/atoms/badge-status.tsx
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

type Status = 'active' | 'inactive' | 'pending' | 'error';

interface BadgeStatusProps {
  status: Status;
  className?: string;
}

const statusConfig: Record<Status, { label: string; className: string }> = {
  active: { label: '활성', className: 'bg-success text-success-foreground' },
  inactive: { label: '비활성', className: 'bg-muted text-muted-foreground' },
  pending: { label: '대기중', className: 'bg-warning text-warning-foreground' },
  error: { label: '오류', className: 'bg-destructive text-destructive-foreground' },
};

export function BadgeStatus({ status, className }: BadgeStatusProps) {
  const config = statusConfig[status];

  return (
    <Badge className={cn(config.className, className)}>
      {config.label}
    </Badge>
  );
}
```

---

## Molecules (조합 컴포넌트)

### Search Bar

```tsx
// components/molecules/search-bar.tsx
'use client';

import { useState, useTransition } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SearchBarProps {
  value?: string;
  onChange?: (value: string) => void;
  onSearch?: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function SearchBar({
  value: controlledValue,
  onChange,
  onSearch,
  placeholder = '검색...',
  className,
}: SearchBarProps) {
  const [internalValue, setInternalValue] = useState('');
  const [isPending, startTransition] = useTransition();

  const value = controlledValue ?? internalValue;
  const setValue = onChange ?? setInternalValue;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    startTransition(() => {
      onSearch?.(value);
    });
  };

  const handleClear = () => {
    setValue('');
    onSearch?.('');
  };

  return (
    <form onSubmit={handleSubmit} className={cn('relative flex gap-2', className)}>
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder}
          className="pl-9 pr-9"
        />
        {value && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2"
            onClick={handleClear}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
      <Button type="submit" disabled={isPending}>
        {isPending ? '검색 중...' : '검색'}
      </Button>
    </form>
  );
}
```

### Form Field

```tsx
// components/molecules/form-field.tsx
import { cn } from '@/lib/utils';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';

interface FormFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  description?: string;
}

export function FormField({
  label,
  error,
  description,
  className,
  id,
  ...props
}: FormFieldProps) {
  const fieldId = id || props.name;

  return (
    <div className={cn('space-y-2', className)}>
      <Label htmlFor={fieldId} className={cn(error && 'text-destructive')}>
        {label}
      </Label>
      <Input
        id={fieldId}
        className={cn(error && 'border-destructive')}
        aria-describedby={error ? `${fieldId}-error` : description ? `${fieldId}-desc` : undefined}
        aria-invalid={!!error}
        {...props}
      />
      {description && !error && (
        <p id={`${fieldId}-desc`} className="text-sm text-muted-foreground">
          {description}
        </p>
      )}
      {error && (
        <p id={`${fieldId}-error`} className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}
```

### User Avatar

```tsx
// components/molecules/user-avatar.tsx
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

interface UserAvatarProps {
  src?: string | null;
  name: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
};

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function UserAvatar({ src, name, size = 'md', className }: UserAvatarProps) {
  return (
    <Avatar className={cn(sizeClasses[size], className)}>
      <AvatarImage src={src ?? undefined} alt={name} />
      <AvatarFallback>{getInitials(name)}</AvatarFallback>
    </Avatar>
  );
}
```

---

## Organisms (복합 컴포넌트)

### Header

```tsx
// components/organisms/header.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { UserAvatar } from '@/components/molecules/user-avatar';
import { ThemeToggle } from '@/components/molecules/theme-toggle';
import { Menu } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HeaderProps {
  user?: {
    name: string;
    email: string;
    avatarUrl?: string;
  };
  onMenuClick?: () => void;
}

export function Header({ user, onMenuClick }: HeaderProps) {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-[var(--header-height)] items-center gap-4">
        {/* Mobile Menu */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onMenuClick}
        >
          <Menu className="h-5 w-5" />
        </Button>

        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <span className="text-xl">Logo</span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-6 ml-6">
          <NavLink href="/dashboard" active={pathname.startsWith('/dashboard')}>
            대시보드
          </NavLink>
          <NavLink href="/users" active={pathname.startsWith('/users')}>
            사용자
          </NavLink>
          <NavLink href="/settings" active={pathname.startsWith('/settings')}>
            설정
          </NavLink>
        </nav>

        {/* Right Side */}
        <div className="ml-auto flex items-center gap-4">
          <ThemeToggle />
          {user && (
            <UserAvatar
              name={user.name}
              src={user.avatarUrl}
              size="sm"
            />
          )}
        </div>
      </div>
    </header>
  );
}

function NavLink({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className={cn(
        'text-sm font-medium transition-colors hover:text-primary',
        active ? 'text-foreground' : 'text-muted-foreground'
      )}
    >
      {children}
    </Link>
  );
}
```

### Sidebar

```tsx
// components/organisms/sidebar.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  LayoutDashboard,
  Users,
  Settings,
  FileText,
  BarChart3,
} from 'lucide-react';

const navigation = [
  { name: '대시보드', href: '/dashboard', icon: LayoutDashboard },
  { name: '사용자', href: '/users', icon: Users },
  { name: '문서', href: '/documents', icon: FileText },
  { name: '분석', href: '/analytics', icon: BarChart3 },
  { name: '설정', href: '/settings', icon: Settings },
];

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
}

export function Sidebar({ open = true, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-[var(--sidebar-width)] border-r bg-background transition-transform duration-300 md:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-[var(--header-height)] items-center border-b px-6">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <span className="text-xl">Logo</span>
          </Link>
        </div>

        <ScrollArea className="h-[calc(100vh-var(--header-height))]">
          <nav className="flex flex-col gap-1 p-4">
            {navigation.map((item) => {
              const isActive = pathname.startsWith(item.href);
              return (
                <Button
                  key={item.href}
                  variant={isActive ? 'secondary' : 'ghost'}
                  className="w-full justify-start gap-3"
                  asChild
                >
                  <Link href={item.href}>
                    <item.icon className="h-4 w-4" />
                    {item.name}
                  </Link>
                </Button>
              );
            })}
          </nav>
        </ScrollArea>
      </aside>
    </>
  );
}
```

---

## Templates (레이아웃)

### Dashboard Layout

```tsx
// components/templates/dashboard-layout.tsx
'use client';

import { useState } from 'react';
import { Header } from '@/components/organisms/header';
import { Sidebar } from '@/components/organisms/sidebar';
import { cn } from '@/lib/utils';

interface DashboardLayoutProps {
  children: React.ReactNode;
  user?: {
    name: string;
    email: string;
    avatarUrl?: string;
  };
}

export function DashboardLayout({ children, user }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="md:pl-[var(--sidebar-width)]">
        <Header
          user={user}
          onMenuClick={() => setSidebarOpen(true)}
        />

        <main className="container py-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

### Auth Layout

```tsx
// components/templates/auth-layout.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  description?: string;
}

export function AuthLayout({ children, title, description }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-2xl font-bold">{title}</CardTitle>
          {description && (
            <CardDescription>{description}</CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {children}
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## Server vs Client Component 가이드

```
┌─────────────────────────────────────────────────────────────┐
│                   Server Components (기본)                   │
│  • 데이터 페칭                                               │
│  • 정적 UI                                                   │
│  • 민감한 데이터 접근 (DB, API keys)                         │
│  • 예: Page, Layout, DataTable (서버에서 데이터 로드)         │
├─────────────────────────────────────────────────────────────┤
│                   Client Components ('use client')           │
│  • 이벤트 핸들러 (onClick, onChange)                         │
│  • useState, useEffect 등 훅 사용                            │
│  • 브라우저 API (localStorage, window)                       │
│  • 예: Form, Modal, Sidebar Toggle, Search                   │
└─────────────────────────────────────────────────────────────┘
```

### 패턴: Server → Client 분리

```tsx
// app/users/page.tsx (Server Component)
import { usersService } from '@/features/users/api/users.service';
import { UsersTable } from '@/features/users/components/users-table';

export default async function UsersPage() {
  const users = await usersService.getUsers(); // 서버에서 데이터 로드

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">사용자 관리</h1>
      <UsersTable initialData={users} /> {/* Client Component에 전달 */}
    </div>
  );
}

// features/users/components/users-table.tsx (Client Component)
'use client';

import { useUsers } from '../hooks/use-users';

export function UsersTable({ initialData }: { initialData: User[] }) {
  const { data: users = initialData } = useUsers(); // 클라이언트에서 재검증

  return (
    <table>{/* ... */}</table>
  );
}
```

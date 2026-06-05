---
name: "shadcn/ui Patterns"
description: "Figma component to shadcn/ui mapping patterns"
---

# Skill: shadcn/ui Patterns

> Figma 컴포넌트를 shadcn/ui로 매핑하는 패턴 라이브러리

---

## 개요

이 스킬은 Figma에서 추출된 컴포넌트를 shadcn/ui 컴포넌트로 매핑합니다.
재사용 가능한 패턴과 커스터마이징 방법을 제공합니다.

---

## 핵심 컴포넌트 매핑

### Button

| Figma 스타일 | shadcn Props |
|--------------|--------------|
| Primary / Filled | `variant="default"` |
| Secondary | `variant="secondary"` |
| Outline / Border | `variant="outline"` |
| Ghost / Text | `variant="ghost"` |
| Link | `variant="link"` |
| Destructive / Danger | `variant="destructive"` |

| Figma 크기 | shadcn Props |
|------------|--------------|
| Small (32px) | `size="sm"` |
| Medium (40px) | `size="default"` |
| Large (48px) | `size="lg"` |
| Icon Only | `size="icon"` |

```tsx
// 사용 예시
import { Button } from '@/components/ui/button';

// Primary Large Button
<Button size="lg">Get Started</Button>

// Outline Button with Icon
<Button variant="outline">
  <Icon className="mr-2 h-4 w-4" />
  Learn More
</Button>

// Icon Button
<Button variant="ghost" size="icon">
  <Menu className="h-4 w-4" />
</Button>
```

---

### Card

| Figma 패턴 | shadcn 구조 |
|------------|-------------|
| 카드 컨테이너 | `<Card>` |
| 카드 상단 영역 | `<CardHeader>` |
| 카드 제목 | `<CardTitle>` |
| 카드 설명 | `<CardDescription>` |
| 카드 본문 | `<CardContent>` |
| 카드 하단 액션 | `<CardFooter>` |

```tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

// Feature Card 패턴
<Card>
  <CardHeader>
    <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
      <Icon className="w-6 h-6 text-primary" />
    </div>
    <CardTitle>Feature Title</CardTitle>
    <CardDescription>Feature description text here.</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Additional content...</p>
  </CardContent>
  <CardFooter>
    <Button variant="outline" className="w-full">Learn More</Button>
  </CardFooter>
</Card>
```

---

### Input & Form

| Figma 패턴 | shadcn 컴포넌트 |
|------------|-----------------|
| 텍스트 입력 | `<Input>` |
| 긴 텍스트 | `<Textarea>` |
| 선택 드롭다운 | `<Select>` |
| 체크박스 | `<Checkbox>` |
| 라디오 버튼 | `<RadioGroup>` |
| 토글 스위치 | `<Switch>` |
| 레이블 | `<Label>` |

```tsx
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

// Form 패턴
<form className="space-y-4">
  <div className="space-y-2">
    <Label htmlFor="email">Email</Label>
    <Input
      id="email"
      type="email"
      placeholder="Enter your email"
    />
  </div>
  <div className="space-y-2">
    <Label htmlFor="password">Password</Label>
    <Input
      id="password"
      type="password"
      placeholder="Enter your password"
    />
  </div>
  <Button type="submit" className="w-full">
    Sign In
  </Button>
</form>
```

---

### Dialog / Modal

| Figma 패턴 | shadcn 구조 |
|------------|-------------|
| 모달 컨테이너 | `<Dialog>` |
| 트리거 버튼 | `<DialogTrigger>` |
| 모달 내용 | `<DialogContent>` |
| 모달 헤더 | `<DialogHeader>` |
| 모달 제목 | `<DialogTitle>` |
| 모달 설명 | `<DialogDescription>` |
| 모달 푸터 | `<DialogFooter>` |

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>
        Dialog description text here.
      </DialogDescription>
    </DialogHeader>
    <div className="py-4">
      {/* Dialog content */}
    </div>
    <DialogFooter>
      <Button variant="outline">Cancel</Button>
      <Button>Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

---

### Navigation

| Figma 패턴 | shadcn 컴포넌트 |
|------------|-----------------|
| 드롭다운 메뉴 | `<DropdownMenu>` |
| 네비게이션 메뉴 | `<NavigationMenu>` |
| 탭 | `<Tabs>` |
| 브레드크럼 | `<Breadcrumb>` |

```tsx
// Tab Navigation
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

<Tabs defaultValue="overview" className="w-full">
  <TabsList className="grid w-full grid-cols-3">
    <TabsTrigger value="overview">Overview</TabsTrigger>
    <TabsTrigger value="features">Features</TabsTrigger>
    <TabsTrigger value="pricing">Pricing</TabsTrigger>
  </TabsList>
  <TabsContent value="overview">Overview content</TabsContent>
  <TabsContent value="features">Features content</TabsContent>
  <TabsContent value="pricing">Pricing content</TabsContent>
</Tabs>
```

---

### Avatar & Badge

```tsx
// Avatar
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

<Avatar>
  <AvatarImage src="/avatar.jpg" alt="User" />
  <AvatarFallback>JD</AvatarFallback>
</Avatar>

// Badge
import { Badge } from '@/components/ui/badge';

<Badge>New</Badge>
<Badge variant="secondary">Popular</Badge>
<Badge variant="outline">Beta</Badge>
<Badge variant="destructive">Deprecated</Badge>
```

---

## 섹션 패턴

### Hero Section

```tsx
export function HeroSection() {
  return (
    <section className="relative py-20 lg:py-32">
      <div className="container mx-auto px-4">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          {/* Content */}
          <div className="flex-1 text-center lg:text-left">
            <Badge className="mb-4">New Release</Badge>
            <h1 className="text-4xl lg:text-6xl font-bold mb-6">
              Build faster with AI
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-xl">
              Transform your Figma designs into production-ready code instantly.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button size="lg">Get Started</Button>
              <Button size="lg" variant="outline">Learn More</Button>
            </div>
          </div>

          {/* Image */}
          <div className="flex-1">
            <Image
              src="/hero-image.png"
              alt="Hero"
              width={600}
              height={400}
              className="rounded-xl shadow-2xl"
              priority
            />
          </div>
        </div>
      </div>
    </section>
  );
}
```

### Feature Grid

```tsx
export function FeatureGrid({ features }: { features: Feature[] }) {
  return (
    <section className="py-20 bg-muted/50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Features</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Everything you need to build modern applications.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <Card key={feature.id}>
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
```

### CTA Section

```tsx
export function CTASection() {
  return (
    <section className="py-20 bg-primary text-primary-foreground">
      <div className="container mx-auto px-4 text-center">
        <h2 className="text-3xl lg:text-4xl font-bold mb-6">
          Ready to get started?
        </h2>
        <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
          Join thousands of developers building with our platform.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" variant="secondary">
            Start Free Trial
          </Button>
          <Button size="lg" variant="outline" className="border-primary-foreground text-primary-foreground hover:bg-primary-foreground hover:text-primary">
            Contact Sales
          </Button>
        </div>
      </div>
    </section>
  );
}
```

### Footer

```tsx
export function Footer() {
  return (
    <footer className="border-t py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {/* Logo & Description */}
          <div className="col-span-2 md:col-span-1">
            <Logo className="mb-4" />
            <p className="text-sm text-muted-foreground">
              Building the future of development.
            </p>
          </div>

          {/* Links */}
          {footerLinks.map((group) => (
            <div key={group.title}>
              <h4 className="font-semibold mb-4">{group.title}</h4>
              <ul className="space-y-2">
                {group.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t mt-12 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} Company. All rights reserved.
          </p>
          <div className="flex gap-4">
            <SocialLinks />
          </div>
        </div>
      </div>
    </footer>
  );
}
```

---

## 커스터마이징

### 테마 확장

```tsx
// tailwind.config.ts
{
  theme: {
    extend: {
      colors: {
        // shadcn 기본 색상 확장
        brand: {
          50: 'var(--brand-50)',
          500: 'var(--brand-500)',
          900: 'var(--brand-900)',
        },
      },
    },
  },
}
```

### 컴포넌트 변형 추가

```tsx
// components/ui/button.tsx
const buttonVariants = cva(
  "...",
  {
    variants: {
      variant: {
        // 기존 variants...
        brand: "bg-brand-500 text-white hover:bg-brand-600",
      },
    },
  }
);
```

---

## 체크리스트

```markdown
## shadcn/ui Integration Checklist

### Setup
- [ ] shadcn/ui 초기화 완료
- [ ] 필요한 컴포넌트 설치
- [ ] 테마 색상 설정

### Components
- [ ] Button variants 매핑
- [ ] Card 구조 적용
- [ ] Input/Form 패턴 적용
- [ ] Dialog 패턴 적용

### Sections
- [ ] Hero 섹션 패턴 적용
- [ ] Feature Grid 패턴 적용
- [ ] CTA 섹션 패턴 적용
- [ ] Footer 패턴 적용

### Customization
- [ ] 브랜드 색상 적용
- [ ] 커스텀 variants 추가
- [ ] 반응형 조정
```

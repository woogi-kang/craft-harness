---
name: form
description: |
  React Hook Form + Zod를 사용하여 폼을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Form Skill

React Hook Form + Zod를 사용하여 폼을 구현합니다.

## Triggers

- "폼", "form", "react-hook-form", "입력 폼"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `formName` | ✅ | 폼 이름 |
| `fields` | ✅ | 필드 목록 |

---

## 설치

```bash
npm install react-hook-form @hookform/resolvers zod
```

---

## 기본 폼 패턴

```tsx
// features/{feature}/components/{feature}-form.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAction } from 'next-safe-action/hooks';
import { toast } from 'sonner';

import { create{Feature}Schema, type Create{Feature}Input } from '../schemas/{feature}.schema';
import { create{Feature}Action } from '../actions/create-{feature}.action';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface {Feature}FormProps {
  defaultValues?: Partial<Create{Feature}Input>;
  onSuccess?: () => void;
}

export function {Feature}Form({ defaultValues, onSuccess }: {Feature}FormProps) {
  const form = useForm<Create{Feature}Input>({
    resolver: zodResolver(create{Feature}Schema),
    defaultValues: {
      title: '',
      description: '',
      status: 'draft',
      ...defaultValues,
    },
  });

  const { execute, isPending } = useAction(create{Feature}Action, {
    onSuccess: () => {
      toast.success('생성되었습니다');
      form.reset();
      onSuccess?.();
    },
    onError: ({ error }) => {
      toast.error(error.serverError || '오류가 발생했습니다');
    },
  });

  const onSubmit = (data: Create{Feature}Input) => {
    execute(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>제목</FormLabel>
              <FormControl>
                <Input placeholder="제목을 입력하세요" {...field} />
              </FormControl>
              <FormDescription>최대 200자</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>설명</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="설명을 입력하세요"
                  className="resize-none"
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="status"
          render={({ field }) => (
            <FormItem>
              <FormLabel>상태</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="상태 선택" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="draft">초안</SelectItem>
                  <SelectItem value="published">발행</SelectItem>
                  <SelectItem value="archived">보관</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isPending}>
          {isPending ? '처리 중...' : '저장'}
        </Button>
      </form>
    </Form>
  );
}
```

---

## 동적 필드 (useFieldArray)

```tsx
'use client';

import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Trash2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormMessage } from '@/components/ui/form';

const formSchema = z.object({
  items: z.array(
    z.object({
      name: z.string().min(1, '필수 입력'),
      quantity: z.coerce.number().min(1, '1개 이상'),
    })
  ).min(1, '최소 1개 항목'),
});

type FormValues = z.infer<typeof formSchema>;

export function DynamicForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { items: [{ name: '', quantity: 1 }] },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'items',
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-4">
        {fields.map((field, index) => (
          <div key={field.id} className="flex gap-2">
            <FormField
              control={form.control}
              name={`items.${index}.name`}
              render={({ field }) => (
                <FormItem className="flex-1">
                  <FormControl>
                    <Input placeholder="항목명" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`items.${index}.quantity`}
              render={({ field }) => (
                <FormItem className="w-24">
                  <FormControl>
                    <Input type="number" min={1} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => remove(index)}
              disabled={fields.length === 1}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}

        <Button type="button" variant="outline" onClick={() => append({ name: '', quantity: 1 })}>
          <Plus className="mr-2 h-4 w-4" /> 항목 추가
        </Button>

        <Button type="submit" className="w-full">저장</Button>
      </form>
    </Form>
  );
}
```

---

## 커스텀 폼 컴포넌트

### Checkbox Group

```tsx
// components/ui/checkbox-group.tsx
'use client';

import { Checkbox } from '@/components/ui/checkbox';
import { FormControl, FormItem, FormLabel } from '@/components/ui/form';

interface Option {
  value: string;
  label: string;
}

interface CheckboxGroupProps {
  options: Option[];
  value: string[];
  onChange: (value: string[]) => void;
}

export function CheckboxGroup({ options, value, onChange }: CheckboxGroupProps) {
  const handleCheckedChange = (checked: boolean, optionValue: string) => {
    if (checked) {
      onChange([...value, optionValue]);
    } else {
      onChange(value.filter((v) => v !== optionValue));
    }
  };

  return (
    <div className="space-y-2">
      {options.map((option) => (
        <FormItem key={option.value} className="flex items-center space-x-2 space-y-0">
          <FormControl>
            <Checkbox
              checked={value.includes(option.value)}
              onCheckedChange={(checked) => handleCheckedChange(!!checked, option.value)}
            />
          </FormControl>
          <FormLabel className="font-normal">{option.label}</FormLabel>
        </FormItem>
      ))}
    </div>
  );
}
```

### Combobox (검색 가능 Select)

```tsx
// components/ui/combobox.tsx
'use client';

import { useState } from 'react';
import { Check, ChevronsUpDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

interface Option {
  value: string;
  label: string;
}

interface ComboboxProps {
  options: Option[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  emptyText?: string;
}

export function Combobox({
  options,
  value,
  onChange,
  placeholder = '선택하세요',
  searchPlaceholder = '검색...',
  emptyText = '결과 없음',
}: ComboboxProps) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between"
        >
          {value ? options.find((o) => o.value === value)?.label : placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput placeholder={searchPlaceholder} />
          <CommandList>
            <CommandEmpty>{emptyText}</CommandEmpty>
            <CommandGroup>
              {options.map((option) => (
                <CommandItem
                  key={option.value}
                  value={option.value}
                  onSelect={(v) => {
                    onChange(v === value ? '' : v);
                    setOpen(false);
                  }}
                >
                  <Check
                    className={cn('mr-2 h-4 w-4', value === option.value ? 'opacity-100' : 'opacity-0')}
                  />
                  {option.label}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
```

---

## 테스트 예제

### 폼 유효성 검증 테스트

```tsx
// features/posts/__tests__/post-form.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PostForm } from '../components/post-form';

vi.mock('next-safe-action/hooks', () => ({
  useAction: () => ({
    execute: vi.fn(),
    isPending: false,
  }),
}));

describe('PostForm', () => {
  it('shows validation errors for empty fields', async () => {
    const user = userEvent.setup();
    render(<PostForm />);

    await user.click(screen.getByRole('button', { name: /저장/i }));

    await waitFor(() => {
      expect(screen.getByText(/제목을 입력하세요/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for short title', async () => {
    const user = userEvent.setup();
    render(<PostForm />);

    await user.type(screen.getByLabelText(/제목/i), 'A');
    await user.click(screen.getByRole('button', { name: /저장/i }));

    await waitFor(() => {
      expect(screen.getByText(/최소/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    const onSuccess = vi.fn();
    const user = userEvent.setup();
    render(<PostForm onSuccess={onSuccess} />);

    await user.type(screen.getByLabelText(/제목/i), 'Valid Title');
    await user.type(screen.getByLabelText(/설명/i), 'Description text');
    await user.click(screen.getByRole('button', { name: /저장/i }));

    // execute가 호출되었는지 확인
  });

  it('clears form after successful submission', async () => {
    const user = userEvent.setup();
    render(<PostForm />);

    await user.type(screen.getByLabelText(/제목/i), 'Test Title');
    // 성공 시뮬레이션 후

    expect(screen.getByLabelText(/제목/i)).toHaveValue('');
  });
});
```

### 동적 필드 테스트

```tsx
// components/__tests__/dynamic-form.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DynamicForm } from '../dynamic-form';

describe('DynamicForm', () => {
  it('adds new field on button click', async () => {
    const user = userEvent.setup();
    render(<DynamicForm />);

    expect(screen.getAllByPlaceholderText('항목명')).toHaveLength(1);

    await user.click(screen.getByRole('button', { name: /항목 추가/i }));

    expect(screen.getAllByPlaceholderText('항목명')).toHaveLength(2);
  });

  it('removes field on delete button click', async () => {
    const user = userEvent.setup();
    render(<DynamicForm />);

    // 항목 2개 추가
    await user.click(screen.getByRole('button', { name: /항목 추가/i }));
    expect(screen.getAllByPlaceholderText('항목명')).toHaveLength(2);

    // 첫 번째 삭제
    const deleteButtons = screen.getAllByRole('button', { name: '' });
    await user.click(deleteButtons[0]);

    expect(screen.getAllByPlaceholderText('항목명')).toHaveLength(1);
  });

  it('prevents removing last item', async () => {
    render(<DynamicForm />);

    const deleteButton = screen.getByRole('button', { name: '' });
    expect(deleteButton).toBeDisabled();
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 제어되지 않는 입력

```tsx
// ❌ Bad: 제어되지 않는 입력 (React Hook Form 미사용)
function Form() {
  const handleSubmit = (e: FormEvent) => {
    const formData = new FormData(e.target);
    // 타입 안전하지 않음
  };
  return <form onSubmit={handleSubmit}><input name="title" /></form>;
}

// ✅ Good: React Hook Form + Zod
function Form() {
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
  });
  return <Form {...form}>{/* 타입 안전 */}</Form>;
}
```

### 2. 인라인 검증 로직

```tsx
// ❌ Bad: 검증 로직 분산
<input
  onChange={(e) => {
    if (e.target.value.length < 3) {
      setError('3자 이상 입력하세요');
    } else if (!/^[a-z]+$/.test(e.target.value)) {
      setError('소문자만 허용됩니다');
    }
  }}
/>

// ✅ Good: Zod 스키마로 중앙화
const schema = z.object({
  title: z.string()
    .min(3, '3자 이상 입력하세요')
    .regex(/^[a-z]+$/, '소문자만 허용됩니다'),
});
```

### 3. 비밀번호 확인 불일치

```typescript
// ❌ Bad: 각 필드 개별 검증
const schema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string().min(8),  // 일치 검증 없음
});

// ✅ Good: refine으로 교차 검증
const schema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: '비밀번호가 일치하지 않습니다',
  path: ['confirmPassword'],
});
```

### 4. 서버 에러 처리 누락

```tsx
// ❌ Bad: 서버 에러 무시
const { execute } = useAction(createAction);
const onSubmit = (data) => execute(data);  // 에러 처리 없음

// ✅ Good: 에러 처리 포함
const { execute } = useAction(createAction, {
  onSuccess: () => {
    toast.success('저장되었습니다');
    form.reset();
  },
  onError: ({ error }) => {
    if (error.validationErrors) {
      // 필드별 에러 설정
      Object.entries(error.validationErrors).forEach(([field, errors]) => {
        form.setError(field, { message: errors[0] });
      });
    } else {
      toast.error(error.serverError || '저장에 실패했습니다');
    }
  },
});
```

---

## 에러 처리

### 서버 검증 에러 표시

```tsx
const { execute } = useAction(createPostAction, {
  onError: ({ error }) => {
    // 서버 검증 에러를 폼 필드에 매핑
    if (error.validationErrors) {
      Object.entries(error.validationErrors).forEach(([field, messages]) => {
        form.setError(field as keyof FormValues, {
          type: 'server',
          message: Array.isArray(messages) ? messages[0] : messages,
        });
      });
    }
  },
});
```

### 네트워크 에러 처리

```tsx
const { execute, status } = useAction(createPostAction, {
  onError: ({ error }) => {
    if (!navigator.onLine) {
      toast.error('인터넷 연결을 확인하세요');
    } else {
      toast.error('서버 연결에 실패했습니다. 다시 시도해주세요.');
    }
  },
});
```

---

## 성능 고려사항

### 입력 디바운스

```tsx
// 검색 폼에서 디바운스
import { useDebouncedCallback } from 'use-debounce';

function SearchForm() {
  const form = useForm();

  const debouncedSearch = useDebouncedCallback((value: string) => {
    router.push(`/search?q=${encodeURIComponent(value)}`);
  }, 300);

  return (
    <FormField
      control={form.control}
      name="query"
      render={({ field }) => (
        <Input
          {...field}
          onChange={(e) => {
            field.onChange(e);
            debouncedSearch(e.target.value);
          }}
        />
      )}
    />
  );
}
```

### 폼 상태 메모이제이션

```tsx
// 복잡한 폼에서 섹션 분리
const PersonalInfoSection = memo(function PersonalInfoSection() {
  const { control } = useFormContext();
  return (/* 개인정보 필드들 */);
});

const AddressSection = memo(function AddressSection() {
  const { control } = useFormContext();
  return (/* 주소 필드들 */);
});
```

---

## 보안 고려사항

### XSS 방지

```tsx
// 사용자 입력 이스케이프
const schema = z.object({
  content: z.string()
    .transform((val) => val.replace(/</g, '&lt;').replace(/>/g, '&gt;')),
});
```

### 민감 정보 자동완성 방지

```tsx
<Input
  type="password"
  autoComplete="new-password"
  {...field}
/>

<Input
  type="text"
  autoComplete="off"
  data-lpignore="true"  // LastPass 무시
  {...field}
/>
```

### 파일 업로드 검증

```typescript
const fileSchema = z.object({
  file: z
    .instanceof(File)
    .refine((f) => f.size <= 5 * 1024 * 1024, '5MB 이하 파일만 허용')
    .refine(
      (f) => ['image/jpeg', 'image/png'].includes(f.type),
      'JPG, PNG만 허용'
    ),
});
```

---

## References

- `_references/SERVER-ACTION-PATTERN.md` - Server Action 패턴
- `_references/TEST-PATTERN.md` - 테스트 피라미드


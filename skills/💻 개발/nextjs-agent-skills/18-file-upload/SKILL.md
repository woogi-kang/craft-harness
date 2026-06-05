---
name: file-upload
description: |
  파일 업로드 기능을 구현합니다 (Vercel Blob, S3, Cloudflare R2).
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# File Upload Skill

파일 업로드 기능을 구현합니다 (Vercel Blob, S3, Cloudflare R2).

## Triggers

- "파일 업로드", "file upload", "이미지 업로드", "blob"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `provider` | ✅ | vercel-blob, s3, cloudflare-r2 |
| `maxSize` | ❌ | 최대 파일 크기 (MB) |

---

## Vercel Blob

### 설치 및 설정

```bash
npm install @vercel/blob
```

```env
# .env.local
BLOB_READ_WRITE_TOKEN=vercel_blob_xxx
```

### Server Action

```typescript
// lib/actions/upload.action.ts
'use server';

import { put, del } from '@vercel/blob';
import { actionClient } from './safe-action';
import { z } from 'zod';

const uploadSchema = z.object({
  filename: z.string(),
  contentType: z.string(),
});

export const uploadFileAction = actionClient
  .schema(uploadSchema)
  .action(async ({ parsedInput }) => {
    // Generate presigned upload URL
    const { url, downloadUrl } = await put(parsedInput.filename, '', {
      access: 'public',
      contentType: parsedInput.contentType,
      addRandomSuffix: true,
    });

    return { uploadUrl: url, downloadUrl };
  });

export const deleteFileAction = actionClient
  .schema(z.object({ url: z.string().url() }))
  .action(async ({ parsedInput }) => {
    await del(parsedInput.url);
    return { success: true };
  });
```

### Upload 컴포넌트

```tsx
// components/ui/file-upload.tsx
'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { upload } from '@vercel/blob/client';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Upload, X, File, Image as ImageIcon } from 'lucide-react';
import { toast } from 'sonner';

interface FileUploadProps {
  onUpload: (url: string) => void;
  accept?: Record<string, string[]>;
  maxSize?: number;
  className?: string;
}

export function FileUpload({
  onUpload,
  accept = { 'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'] },
  maxSize = 10 * 1024 * 1024, // 10MB
  className,
}: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleUpload = useCallback(
    async (file: File) => {
      setUploading(true);
      setProgress(0);

      try {
        const blob = await upload(file.name, file, {
          access: 'public',
          handleUploadUrl: '/api/upload',
          onUploadProgress: ({ percentage }) => {
            setProgress(percentage);
          },
        });

        onUpload(blob.url);
        toast.success('업로드 완료');
      } catch (error) {
        console.error(error);
        toast.error('업로드 실패');
      } finally {
        setUploading(false);
        setProgress(0);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept,
    maxSize,
    multiple: false,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles[0]) handleUpload(acceptedFiles[0]);
    },
    onDropRejected: (rejections) => {
      const error = rejections[0]?.errors[0];
      if (error?.code === 'file-too-large') {
        toast.error(`파일 크기는 ${maxSize / 1024 / 1024}MB 이하여야 합니다`);
      } else {
        toast.error('지원하지 않는 파일 형식입니다');
      }
    },
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
        isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50',
        uploading && 'pointer-events-none opacity-50',
        className
      )}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <div className="space-y-4">
          <Progress value={progress} className="w-full" />
          <p className="text-sm text-muted-foreground">업로드 중... {progress}%</p>
        </div>
      ) : (
        <div className="space-y-2">
          <Upload className="mx-auto h-10 w-10 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            {isDragActive ? '파일을 놓으세요' : '파일을 드래그하거나 클릭하여 업로드'}
          </p>
          <p className="text-xs text-muted-foreground">
            최대 {maxSize / 1024 / 1024}MB
          </p>
        </div>
      )}
    </div>
  );
}
```

### API Route (Client Upload)

```typescript
// app/api/upload/route.ts
import { handleUpload, type HandleUploadBody } from '@vercel/blob/client';
import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

export async function POST(request: Request): Promise<NextResponse> {
  const body = (await request.json()) as HandleUploadBody;

  try {
    const jsonResponse = await handleUpload({
      body,
      request,
      onBeforeGenerateToken: async (pathname) => {
        // Auth check
        const session = await auth();
        if (!session) throw new Error('Unauthorized');

        return {
          allowedContentTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
          maximumSizeInBytes: 10 * 1024 * 1024, // 10MB
        };
      },
      onUploadCompleted: async ({ blob }) => {
        // DB에 저장하는 로직
        console.log('Upload completed:', blob.url);
      },
    });

    return NextResponse.json(jsonResponse);
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 400 });
  }
}
```

---

## 이미지 미리보기

```tsx
// components/ui/image-upload.tsx
'use client';

import { useState } from 'react';
import Image from 'next/image';
import { FileUpload } from './file-upload';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

interface ImageUploadProps {
  value?: string;
  onChange: (url: string | undefined) => void;
}

export function ImageUpload({ value, onChange }: ImageUploadProps) {
  if (value) {
    return (
      <div className="relative aspect-video w-full max-w-md overflow-hidden rounded-lg border">
        <Image src={value} alt="Uploaded" fill className="object-cover" />
        <Button
          variant="destructive"
          size="icon"
          className="absolute right-2 top-2"
          onClick={() => onChange(undefined)}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return <FileUpload onUpload={onChange} />;
}
```

---

## 다중 파일 업로드

```tsx
// components/ui/multi-file-upload.tsx
'use client';

import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { upload } from '@vercel/blob/client';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Upload, X, File } from 'lucide-react';
import { toast } from 'sonner';

interface UploadedFile {
  name: string;
  url: string;
  size: number;
}

interface MultiFileUploadProps {
  value: UploadedFile[];
  onChange: (files: UploadedFile[]) => void;
  maxFiles?: number;
  maxSize?: number;
}

export function MultiFileUpload({
  value,
  onChange,
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024,
}: MultiFileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState<Record<string, number>>({});

  const handleUpload = async (files: File[]) => {
    setUploading(true);

    const uploaded: UploadedFile[] = [];

    for (const file of files) {
      try {
        const blob = await upload(file.name, file, {
          access: 'public',
          handleUploadUrl: '/api/upload',
          onUploadProgress: ({ percentage }) => {
            setProgress((prev) => ({ ...prev, [file.name]: percentage }));
          },
        });

        uploaded.push({ name: file.name, url: blob.url, size: file.size });
      } catch (error) {
        toast.error(`${file.name} 업로드 실패`);
      }
    }

    onChange([...value, ...uploaded]);
    setUploading(false);
    setProgress({});
  };

  const handleRemove = (url: string) => {
    onChange(value.filter((f) => f.url !== url));
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    maxFiles: maxFiles - value.length,
    maxSize,
    multiple: true,
    disabled: value.length >= maxFiles || uploading,
    onDrop: handleUpload,
  });

  return (
    <div className="space-y-4">
      {/* Uploaded Files */}
      {value.length > 0 && (
        <div className="space-y-2">
          {value.map((file) => (
            <div
              key={file.url}
              className="flex items-center justify-between rounded-lg border p-3"
            >
              <div className="flex items-center gap-3">
                <File className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => handleRemove(file.url)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Upload Zone */}
      {value.length < maxFiles && (
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
            isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25',
            uploading && 'pointer-events-none opacity-50'
          )}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-8 w-8 text-muted-foreground" />
          <p className="mt-2 text-sm text-muted-foreground">
            파일 업로드 ({value.length}/{maxFiles})
          </p>
        </div>
      )}

      {/* Upload Progress */}
      {Object.keys(progress).length > 0 && (
        <div className="space-y-2">
          {Object.entries(progress).map(([name, percent]) => (
            <div key={name} className="space-y-1">
              <p className="text-xs text-muted-foreground">{name}</p>
              <Progress value={percent} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Form 연동

```tsx
// 폼에서 사용
<FormField
  control={form.control}
  name="image"
  render={({ field }) => (
    <FormItem>
      <FormLabel>이미지</FormLabel>
      <FormControl>
        <ImageUpload value={field.value} onChange={field.onChange} />
      </FormControl>
      <FormMessage />
    </FormItem>
  )}
/>
```

---

## 테스트 예제

### Upload API 테스트

```typescript
// app/api/upload/__tests__/route.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { POST } from '../route';
import { auth } from '@/lib/auth';

vi.mock('@/lib/auth');
vi.mock('@vercel/blob/client', () => ({
  handleUpload: vi.fn(),
}));

describe('POST /api/upload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should reject unauthorized requests', async () => {
    vi.mocked(auth).mockResolvedValue(null);

    const request = new Request('http://localhost/api/upload', {
      method: 'POST',
      body: JSON.stringify({ type: 'blob.generate-client-token' }),
    });

    const response = await POST(request);

    expect(response.status).toBe(400); // handleUpload throws
  });

  it('should validate file type', async () => {
    vi.mocked(auth).mockResolvedValue({ user: { id: '1' } });

    const { handleUpload } = await import('@vercel/blob/client');
    vi.mocked(handleUpload).mockImplementation(async ({ onBeforeGenerateToken }) => {
      const result = await onBeforeGenerateToken?.('test.exe');
      expect(result?.allowedContentTypes).not.toContain('application/x-executable');
      return { type: 'blob.upload-complete', url: 'https://...' };
    });

    const request = new Request('http://localhost/api/upload', {
      method: 'POST',
      body: JSON.stringify({ type: 'blob.generate-client-token', pathname: 'test.exe' }),
    });

    await POST(request);
  });

  it('should enforce max file size', async () => {
    vi.mocked(auth).mockResolvedValue({ user: { id: '1' } });

    const { handleUpload } = await import('@vercel/blob/client');
    vi.mocked(handleUpload).mockImplementation(async ({ onBeforeGenerateToken }) => {
      const result = await onBeforeGenerateToken?.('test.jpg');
      expect(result?.maximumSizeInBytes).toBeLessThanOrEqual(10 * 1024 * 1024);
      return { type: 'blob.upload-complete', url: 'https://...' };
    });

    const request = new Request('http://localhost/api/upload', {
      method: 'POST',
      body: JSON.stringify({ type: 'blob.generate-client-token', pathname: 'test.jpg' }),
    });

    await POST(request);
  });
});
```

### FileUpload 컴포넌트 테스트

```typescript
// components/ui/__tests__/file-upload.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileUpload } from '../file-upload';
import { upload } from '@vercel/blob/client';

vi.mock('@vercel/blob/client', () => ({
  upload: vi.fn(),
}));

describe('FileUpload', () => {
  it('should render dropzone', () => {
    render(<FileUpload onUpload={vi.fn()} />);

    expect(screen.getByText(/드래그하거나 클릭/i)).toBeInTheDocument();
  });

  it('should show progress during upload', async () => {
    const user = userEvent.setup();
    let progressCallback: (args: { percentage: number }) => void;

    vi.mocked(upload).mockImplementation(async (_, __, options) => {
      progressCallback = options?.onUploadProgress as any;
      await new Promise((resolve) => setTimeout(resolve, 100));
      progressCallback?.({ percentage: 50 });
      await new Promise((resolve) => setTimeout(resolve, 100));
      return { url: 'https://test.com/file.jpg' };
    });

    const onUpload = vi.fn();
    render(<FileUpload onUpload={onUpload} />);

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const input = screen.getByRole('presentation').querySelector('input')!;

    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText(/업로드 중/i)).toBeInTheDocument();
    });
  });

  it('should reject files exceeding max size', async () => {
    const user = userEvent.setup();
    const onUpload = vi.fn();

    render(<FileUpload onUpload={onUpload} maxSize={1024} />); // 1KB limit

    // Create a file larger than 1KB
    const largeFile = new File(['x'.repeat(2048)], 'large.jpg', { type: 'image/jpeg' });
    const input = screen.getByRole('presentation').querySelector('input')!;

    await user.upload(input, largeFile);

    // Upload should not be called
    expect(upload).not.toHaveBeenCalled();
  });

  it('should call onUpload with URL on success', async () => {
    const user = userEvent.setup();
    vi.mocked(upload).mockResolvedValue({ url: 'https://test.com/file.jpg' });

    const onUpload = vi.fn();
    render(<FileUpload onUpload={onUpload} />);

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const input = screen.getByRole('presentation').querySelector('input')!;

    await user.upload(input, file);

    await waitFor(() => {
      expect(onUpload).toHaveBeenCalledWith('https://test.com/file.jpg');
    });
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 파일 타입 미검증

```typescript
// ❌ Bad: 모든 파일 허용
export async function POST(request: Request) {
  const formData = await request.formData();
  const file = formData.get('file') as File;
  await put(file.name, file, { access: 'public' });  // 위험!
}

// ✅ Good: Content-Type 화이트리스트
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

export async function POST(request: Request) {
  const formData = await request.formData();
  const file = formData.get('file') as File;

  if (!ALLOWED_TYPES.includes(file.type)) {
    return NextResponse.json({ error: '지원하지 않는 파일 형식입니다' }, { status: 400 });
  }

  await put(file.name, file, { access: 'public' });
}
```

### 2. 파일명 미처리

```typescript
// ❌ Bad: 원본 파일명 그대로 사용
await put(file.name, file, { access: 'public' });  // XSS, 경로 탐색 위험

// ✅ Good: 랜덤 suffix 추가
await put(file.name, file, {
  access: 'public',
  addRandomSuffix: true,  // 파일명 충돌 방지 + 보안
});
```

### 3. 대용량 파일 메모리 로드

```typescript
// ❌ Bad: 전체 파일을 메모리에 로드
const buffer = await file.arrayBuffer();
await put(fileName, buffer, { access: 'public' });

// ✅ Good: 스트리밍 업로드 (클라이언트 직접 업로드)
// 서버는 토큰만 발급, 클라이언트가 직접 Blob Storage로 업로드
await upload(file.name, file, {
  handleUploadUrl: '/api/upload',  // 토큰 발급 엔드포인트
});
```

### 4. 삭제 권한 미확인

```typescript
// ❌ Bad: 누구나 삭제 가능
export const deleteFileAction = actionClient
  .schema(z.object({ url: z.string().url() }))
  .action(async ({ parsedInput }) => {
    await del(parsedInput.url);  // 다른 사용자 파일도 삭제 가능!
  });

// ✅ Good: 소유권 확인
export const deleteFileAction = authActionClient
  .schema(z.object({ url: z.string().url() }))
  .action(async ({ parsedInput, ctx }) => {
    // DB에서 파일 소유자 확인
    const file = await db.query.files.findFirst({
      where: eq(files.url, parsedInput.url),
    });

    if (!file || file.userId !== ctx.user.id) {
      throw new ActionError('권한이 없습니다', 'FORBIDDEN');
    }

    await del(parsedInput.url);
  });
```

---

## 에러 처리

### 업로드 에러 타입

```typescript
// lib/errors/upload.ts
export class UploadError extends Error {
  constructor(
    message: string,
    public code: UploadErrorCode,
    public statusCode = 400
  ) {
    super(message);
    this.name = 'UploadError';
  }
}

export type UploadErrorCode =
  | 'INVALID_FILE_TYPE'
  | 'FILE_TOO_LARGE'
  | 'UPLOAD_FAILED'
  | 'STORAGE_ERROR'
  | 'UNAUTHORIZED';

export function validateFile(file: File, options: {
  allowedTypes: string[];
  maxSize: number;
}) {
  if (!options.allowedTypes.includes(file.type)) {
    throw new UploadError(
      `지원하지 않는 파일 형식입니다. 허용: ${options.allowedTypes.join(', ')}`,
      'INVALID_FILE_TYPE'
    );
  }

  if (file.size > options.maxSize) {
    throw new UploadError(
      `파일 크기는 ${options.maxSize / 1024 / 1024}MB 이하여야 합니다`,
      'FILE_TOO_LARGE'
    );
  }
}
```

### 클라이언트 에러 핸들링

```tsx
const handleUpload = async (file: File) => {
  try {
    const blob = await upload(file.name, file, {
      access: 'public',
      handleUploadUrl: '/api/upload',
    });
    onUpload(blob.url);
    toast.success('업로드 완료');
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('size')) {
        toast.error('파일이 너무 큽니다');
      } else if (error.message.includes('type')) {
        toast.error('지원하지 않는 파일 형식입니다');
      } else if (error.message.includes('Unauthorized')) {
        toast.error('로그인이 필요합니다');
      } else {
        toast.error('업로드에 실패했습니다');
      }
    }
    console.error('[Upload Error]:', error);
  }
};
```

---

## 성능 고려사항

### 클라이언트 직접 업로드

```typescript
// 서버 부하 최소화: 서버는 토큰만 발급
// 파일은 클라이언트 → Blob Storage 직접 전송

// API Route (토큰 발급만)
export async function POST(request: Request) {
  return handleUpload({
    body,
    request,
    onBeforeGenerateToken: async () => ({
      allowedContentTypes: ['image/*'],
      maximumSizeInBytes: 10 * 1024 * 1024,
    }),
  });
}
```

### 이미지 최적화

```typescript
// 업로드 후 이미지 최적화 (Sharp 또는 Cloudinary)
import sharp from 'sharp';

async function optimizeImage(buffer: Buffer): Promise<Buffer> {
  return sharp(buffer)
    .resize(1920, 1080, { fit: 'inside', withoutEnlargement: true })
    .webp({ quality: 80 })
    .toBuffer();
}
```

### 병렬 업로드

```typescript
// 다중 파일 병렬 업로드
const uploadMultiple = async (files: File[]) => {
  const results = await Promise.allSettled(
    files.map((file) => upload(file.name, file, { handleUploadUrl: '/api/upload' }))
  );

  const succeeded = results.filter((r) => r.status === 'fulfilled');
  const failed = results.filter((r) => r.status === 'rejected');

  if (failed.length > 0) {
    toast.warning(`${failed.length}개 파일 업로드 실패`);
  }

  return succeeded.map((r) => (r as PromiseFulfilledResult<any>).value);
};
```

---

## 보안 고려사항

### Content-Type 검증

```typescript
// MIME 타입 위조 방지 - Magic Number 검증
async function validateMagicNumber(file: File): Promise<boolean> {
  const buffer = await file.slice(0, 8).arrayBuffer();
  const bytes = new Uint8Array(buffer);

  const signatures: Record<string, number[]> = {
    'image/jpeg': [0xff, 0xd8, 0xff],
    'image/png': [0x89, 0x50, 0x4e, 0x47],
    'image/gif': [0x47, 0x49, 0x46],
    'image/webp': [0x52, 0x49, 0x46, 0x46], // RIFF
  };

  const expectedSignature = signatures[file.type];
  if (!expectedSignature) return false;

  return expectedSignature.every((byte, i) => bytes[i] === byte);
}
```

### 악성 파일 방지

```typescript
const DANGEROUS_EXTENSIONS = ['.exe', '.bat', '.cmd', '.sh', '.php', '.js', '.html'];

function sanitizeFilename(filename: string): string {
  // 경로 탐색 방지
  const sanitized = filename.replace(/[/\\]/g, '_');

  // 위험한 확장자 차단
  const ext = sanitized.slice(sanitized.lastIndexOf('.'));
  if (DANGEROUS_EXTENSIONS.includes(ext.toLowerCase())) {
    throw new UploadError('허용되지 않는 파일 형식입니다', 'INVALID_FILE_TYPE');
  }

  return sanitized;
}
```

### 스토리지 접근 제어

```typescript
// Vercel Blob: 기본적으로 public URL
// 민감한 파일은 signed URL 사용

import { getSignedUrl } from '@vercel/blob';

// 제한 시간 URL 생성
const signedUrl = await getSignedUrl(blobUrl, {
  expiresIn: 60 * 60, // 1시간
});
```

### Rate Limiting

```typescript
// 업로드 남용 방지
const uploadRateLimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '1 h'),  // 시간당 10개
});

export async function POST(request: Request) {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { success } = await uploadRateLimit.limit(`upload:${session.user.id}`);
  if (!success) {
    return NextResponse.json({ error: '업로드 한도 초과' }, { status: 429 });
  }

  // ... upload logic
}
```

---

## References

- `_references/SERVER-ACTION-PATTERN.md`
- `_references/TEST-PATTERN.md`


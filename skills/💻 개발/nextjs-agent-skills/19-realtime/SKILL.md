---
name: realtime
description: |
  실시간 기능을 구현합니다 (Server-Sent Events, WebSocket, Pusher).
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Realtime Skill

실시간 기능을 구현합니다 (Server-Sent Events, WebSocket, Pusher).

## Triggers

- "실시간", "realtime", "sse", "websocket", "pusher"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `type` | ✅ | sse, websocket, pusher |
| `features` | ❌ | notifications, chat, presence |

---

## Server-Sent Events (SSE)

### API Route

```typescript
// app/api/notifications/stream/route.ts
import { auth } from '@/lib/auth';

export const runtime = 'nodejs';

export async function GET(request: Request) {
  const session = await auth();
  if (!session) {
    return new Response('Unauthorized', { status: 401 });
  }

  const encoder = new TextEncoder();
  let interval: NodeJS.Timeout | null = null;
  let heartbeat: NodeJS.Timeout | null = null;
  let isClosed = false;

  const stream = new ReadableStream({
    async start(controller) {
      const sendEvent = (data: unknown) => {
        if (isClosed) return;
        try {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
        } catch {
          // Controller already closed
          cleanup();
        }
      };

      const cleanup = () => {
        if (isClosed) return;
        isClosed = true;
        if (interval) {
          clearInterval(interval);
          interval = null;
        }
        if (heartbeat) {
          clearInterval(heartbeat);
          heartbeat = null;
        }
        try {
          controller.close();
        } catch {
          // Already closed
        }
      };

      // Initial connection
      sendEvent({ type: 'connected', userId: session.user.id });

      // Heartbeat to detect disconnection (every 30s)
      heartbeat = setInterval(() => {
        sendEvent({ type: 'heartbeat', timestamp: Date.now() });
      }, 30000);

      // Polling interval (or DB listener)
      interval = setInterval(async () => {
        if (isClosed) return;
        try {
          const notifications = await getNewNotifications(session.user.id);
          if (notifications.length > 0) {
            sendEvent({ type: 'notifications', data: notifications });
          }
        } catch (error) {
          console.error('Failed to fetch notifications:', error);
        }
      }, 5000);

      // Handle client disconnect via AbortSignal
      request.signal.addEventListener('abort', () => {
        cleanup();
      });
    },
    cancel() {
      // Called when the stream is cancelled by the client
      isClosed = true;
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
      if (heartbeat) {
        clearInterval(heartbeat);
        heartbeat = null;
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no', // Disable nginx buffering
    },
  });
}
```

### SSE Client Hook

```typescript
// hooks/use-sse.ts
'use client';

import { useEffect, useRef, useState } from 'react';

interface UseSSEOptions<T> {
  url: string;
  onMessage?: (data: T) => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
}

export function useSSE<T>({ url, onMessage, onError, reconnectInterval = 3000 }: UseSSEOptions<T>) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<T | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const connect = () => {
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
      };

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data) as T;
        setLastMessage(data);
        onMessage?.(data);
      };

      eventSource.onerror = (error) => {
        setIsConnected(false);
        onError?.(error);
        eventSource.close();

        // Reconnect
        reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
      };
    };

    connect();

    return () => {
      eventSourceRef.current?.close();
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [url, onMessage, onError, reconnectInterval]);

  return { isConnected, lastMessage };
}
```

### Notification 컴포넌트

```tsx
// features/notifications/components/notification-listener.tsx
'use client';

import { useEffect } from 'react';
import { useSSE } from '@/hooks/use-sse';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

interface NotificationEvent {
  type: 'connected' | 'notifications';
  data?: Notification[];
}

export function NotificationListener() {
  const queryClient = useQueryClient();

  const { isConnected } = useSSE<NotificationEvent>({
    url: '/api/notifications/stream',
    onMessage: (event) => {
      if (event.type === 'notifications' && event.data) {
        // Invalidate notifications query
        queryClient.invalidateQueries({ queryKey: ['notifications'] });

        // Show toast for new notifications
        event.data.forEach((notification) => {
          toast(notification.title, {
            description: notification.message,
          });
        });
      }
    },
  });

  // Connection status indicator (optional)
  useEffect(() => {
    if (!isConnected) {
      console.log('SSE: Reconnecting...');
    }
  }, [isConnected]);

  return null; // This is a listener component
}
```

---

## WebSocket (ws)

Next.js는 기본적으로 WebSocket을 지원하지 않지만, Custom Server 또는 별도 WS 서버로 구현 가능합니다.

### 설치

```bash
npm install ws
npm install -D @types/ws
```

### Standalone WebSocket Server

```typescript
// server/websocket.ts
import { WebSocketServer, WebSocket } from 'ws';
import { createServer } from 'http';
import { parse } from 'url';
import next from 'next';

const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev });
const handle = app.getRequestHandler();

// Connection 관리
const clients = new Map<string, Set<WebSocket>>();

app.prepare().then(() => {
  const server = createServer((req, res) => {
    const parsedUrl = parse(req.url!, true);
    handle(req, res, parsedUrl);
  });

  const wss = new WebSocketServer({ server, path: '/ws' });

  wss.on('connection', (ws, req) => {
    const url = new URL(req.url!, `http://${req.headers.host}`);
    const userId = url.searchParams.get('userId');
    const roomId = url.searchParams.get('roomId');

    if (!userId || !roomId) {
      ws.close(1008, 'Missing userId or roomId');
      return;
    }

    // Room에 추가
    if (!clients.has(roomId)) {
      clients.set(roomId, new Set());
    }
    clients.get(roomId)!.add(ws);

    console.log(`User ${userId} joined room ${roomId}`);

    // 메시지 처리
    ws.on('message', (data) => {
      const message = JSON.parse(data.toString());

      // Broadcast to room (자신 제외)
      const room = clients.get(roomId);
      if (room) {
        room.forEach((client) => {
          if (client !== ws && client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({
              type: message.type,
              data: message.data,
              userId,
              timestamp: new Date().toISOString(),
            }));
          }
        });
      }
    });

    // Heartbeat
    const heartbeat = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.ping();
      }
    }, 30000);

    ws.on('close', () => {
      clients.get(roomId)?.delete(ws);
      clearInterval(heartbeat);
      console.log(`User ${userId} left room ${roomId}`);
    });

    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  });

  const PORT = parseInt(process.env.PORT || '3000', 10);
  server.listen(PORT, () => {
    console.log(`> Ready on http://localhost:${PORT}`);
    console.log(`> WebSocket server on ws://localhost:${PORT}/ws`);
  });
});
```

### package.json 스크립트

```json
{
  "scripts": {
    "dev": "tsx watch server/websocket.ts",
    "build": "next build",
    "start": "NODE_ENV=production tsx server/websocket.ts"
  }
}
```

### WebSocket Client Hook

```typescript
// hooks/use-websocket.ts
'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: unknown) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxRetries?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  send: (data: unknown) => void;
  disconnect: () => void;
}

export function useWebSocket({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  reconnectInterval = 3000,
  maxRetries = 5,
}: UseWebSocketOptions): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      retriesRef.current = 0;
      onOpen?.();
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    };

    ws.onclose = () => {
      setIsConnected(false);
      onClose?.();

      // Reconnect logic
      if (retriesRef.current < maxRetries) {
        retriesRef.current++;
        reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
      }
    };

    ws.onerror = (error) => {
      onError?.(error);
    };
  }, [url, onMessage, onOpen, onClose, onError, reconnectInterval, maxRetries]);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    retriesRef.current = maxRetries; // Prevent reconnect
    wsRef.current?.close();
  }, [maxRetries]);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { isConnected, send, disconnect };
}
```

### Chat 컴포넌트 (WebSocket)

```tsx
// features/chat/components/ws-chat-room.tsx
'use client';

import { useState, useCallback } from 'react';
import { useWebSocket } from '@/hooks/use-websocket';

interface Message {
  type: 'message';
  data: { content: string };
  userId: string;
  timestamp: string;
}

interface WSChatRoomProps {
  roomId: string;
  userId: string;
}

export function WSChatRoom({ roomId, userId }: WSChatRoomProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws?userId=${userId}&roomId=${roomId}`;

  const handleMessage = useCallback((data: unknown) => {
    const message = data as Message;
    if (message.type === 'message') {
      setMessages((prev) => [...prev, message]);
    }
  }, []);

  const { isConnected, send } = useWebSocket({
    url: wsUrl,
    onMessage: handleMessage,
  });

  const handleSend = () => {
    if (!input.trim()) return;

    send({ type: 'message', data: { content: input } });

    // 자신의 메시지도 표시
    setMessages((prev) => [
      ...prev,
      {
        type: 'message',
        data: { content: input },
        userId,
        timestamp: new Date().toISOString(),
      },
    ]);
    setInput('');
  };

  return (
    <div className="flex h-full flex-col">
      <div className="mb-2 flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-sm text-gray-500">
          {isConnected ? '연결됨' : '연결 중...'}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`rounded p-2 ${
              msg.userId === userId ? 'ml-auto bg-blue-100' : 'bg-gray-100'
            } max-w-[80%]`}
          >
            <p>{msg.data.content}</p>
            <span className="text-xs text-gray-400">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1 rounded border p-2"
          placeholder="메시지 입력..."
          disabled={!isConnected}
        />
        <button
          onClick={handleSend}
          disabled={!isConnected}
          className="rounded bg-blue-500 px-4 py-2 text-white disabled:opacity-50"
        >
          전송
        </button>
      </div>
    </div>
  );
}
```

### Vercel 배포 시 대안

> ⚠️ **Vercel은 WebSocket을 지원하지 않음**
>
> Vercel에서 실시간 기능이 필요한 경우:
> - **SSE (Server-Sent Events)**: 단방향 실시간 (위 섹션 참조)
> - **Pusher/Ably**: 관리형 WebSocket 서비스 (아래 섹션 참조)
> - **별도 WS 서버**: Railway, Fly.io, AWS EC2 등에 배포

---

## Pusher (권장)

### 설치 및 설정

```bash
npm install pusher pusher-js
```

```env
# .env.local
PUSHER_APP_ID=xxx
PUSHER_KEY=xxx
PUSHER_SECRET=xxx
PUSHER_CLUSTER=ap3

NEXT_PUBLIC_PUSHER_KEY=xxx
NEXT_PUBLIC_PUSHER_CLUSTER=ap3
```

### Server Client

```typescript
// lib/pusher/server.ts
import Pusher from 'pusher';

export const pusher = new Pusher({
  appId: process.env.PUSHER_APP_ID!,
  key: process.env.PUSHER_KEY!,
  secret: process.env.PUSHER_SECRET!,
  cluster: process.env.PUSHER_CLUSTER!,
  useTLS: true,
});
```

### Client Setup

```typescript
// lib/pusher/client.ts
import PusherClient from 'pusher-js';

let pusherClient: PusherClient | null = null;

export function getPusherClient() {
  if (!pusherClient) {
    pusherClient = new PusherClient(process.env.NEXT_PUBLIC_PUSHER_KEY!, {
      cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER!,
    });
  }
  return pusherClient;
}
```

### Pusher Hook

```typescript
// hooks/use-pusher.ts
'use client';

import { useEffect, useRef, useCallback } from 'react';
import type { Channel } from 'pusher-js';
import { getPusherClient } from '@/lib/pusher/client';

interface UsePusherOptions<T> {
  channel: string;
  event: string;
  onEvent: (data: T) => void;
}

export function usePusher<T>({ channel: channelName, event, onEvent }: UsePusherOptions<T>) {
  const channelRef = useRef<Channel | null>(null);
  // useRef로 onEvent를 감싸서 의존성 배열에서 제외 (무한 루프 방지)
  const onEventRef = useRef(onEvent);

  // onEvent가 변경될 때 ref 업데이트
  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    const pusher = getPusherClient();
    const channel = pusher.subscribe(channelName);
    channelRef.current = channel;

    // ref를 통해 최신 콜백 호출
    const handler = (data: T) => onEventRef.current(data);
    channel.bind(event, handler);

    return () => {
      channel.unbind(event, handler);
      pusher.unsubscribe(channelName);
    };
  }, [channelName, event]); // onEvent 제거
}
```

### Server-side Trigger

```typescript
// features/messages/actions/send-message.action.ts
'use server';

import { pusher } from '@/lib/pusher/server';
import { authActionClient } from '@/lib/actions/safe-action';
import { z } from 'zod';

const sendMessageSchema = z.object({
  channelId: z.string(),
  content: z.string().min(1).max(1000),
});

export const sendMessageAction = authActionClient
  .schema(sendMessageSchema)
  .action(async ({ parsedInput, ctx }) => {
    const { channelId, content } = parsedInput;

    // Save to DB
    const message = await db.insert(messages).values({
      channelId,
      content,
      userId: ctx.user.id,
    }).returning();

    // Trigger Pusher event
    await pusher.trigger(`channel-${channelId}`, 'new-message', {
      id: message[0].id,
      content,
      user: { id: ctx.user.id, name: ctx.user.name },
      createdAt: new Date().toISOString(),
    });

    return message[0];
  });
```

### Chat 컴포넌트

```tsx
// features/chat/components/chat-room.tsx
'use client';

import { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { usePusher } from '@/hooks/use-pusher';
import { MessageList } from './message-list';
import { MessageInput } from './message-input';

interface Message {
  id: string;
  content: string;
  user: { id: string; name: string };
  createdAt: string;
}

interface ChatRoomProps {
  channelId: string;
}

export function ChatRoom({ channelId }: ChatRoomProps) {
  const queryClient = useQueryClient();

  // Fetch initial messages
  const { data: messages = [] } = useQuery({
    queryKey: ['messages', channelId],
    queryFn: () => fetch(`/api/channels/${channelId}/messages`).then((r) => r.json()),
  });

  // Listen for new messages
  const handleNewMessage = useCallback(
    (message: Message) => {
      queryClient.setQueryData(['messages', channelId], (old: Message[] = []) => [
        ...old,
        message,
      ]);
    },
    [queryClient, channelId]
  );

  usePusher<Message>({
    channel: `channel-${channelId}`,
    event: 'new-message',
    onEvent: handleNewMessage,
  });

  return (
    <div className="flex h-full flex-col">
      <MessageList messages={messages} />
      <MessageInput channelId={channelId} />
    </div>
  );
}
```

---

## Presence Channel (온라인 상태)

```typescript
// hooks/use-presence.ts
'use client';

import { useEffect, useState } from 'react';
import { getPusherClient } from '@/lib/pusher/client';
import type { PresenceChannel, Members } from 'pusher-js';

interface Member {
  id: string;
  info: { name: string; avatar?: string };
}

export function usePresence(channelName: string) {
  const [members, setMembers] = useState<Member[]>([]);

  useEffect(() => {
    const pusher = getPusherClient();
    const channel = pusher.subscribe(`presence-${channelName}`) as PresenceChannel;

    channel.bind('pusher:subscription_succeeded', (membersData: Members) => {
      const memberList: Member[] = [];
      membersData.each((member: Member) => memberList.push(member));
      setMembers(memberList);
    });

    channel.bind('pusher:member_added', (member: Member) => {
      setMembers((prev) => [...prev, member]);
    });

    channel.bind('pusher:member_removed', (member: Member) => {
      setMembers((prev) => prev.filter((m) => m.id !== member.id));
    });

    return () => {
      pusher.unsubscribe(`presence-${channelName}`);
    };
  }, [channelName]);

  return members;
}
```

### Presence Auth Route

```typescript
// app/api/pusher/auth/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { pusher } from '@/lib/pusher/server';

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const formData = await request.formData();
  const socketId = formData.get('socket_id') as string;
  const channel = formData.get('channel_name') as string;

  const authResponse = pusher.authorizeChannel(socketId, channel, {
    user_id: session.user.id,
    user_info: {
      name: session.user.name,
      avatar: session.user.image,
    },
  });

  return NextResponse.json(authResponse);
}
```

---

## 테스트 예제

### SSE Hook 테스트

```typescript
// hooks/__tests__/use-sse.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useSSE } from '../use-sse';

// EventSource mock
class MockEventSource {
  static instances: MockEventSource[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onerror: ((error: Event) => void) | null = null;
  readyState = 0;

  constructor(public url: string) {
    MockEventSource.instances.push(this);
  }

  close = vi.fn();

  // 테스트용 헬퍼
  simulateOpen() {
    this.readyState = 1;
    this.onopen?.();
  }

  simulateMessage(data: unknown) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }

  simulateError() {
    this.onerror?.(new Event('error'));
  }
}

describe('useSSE', () => {
  beforeEach(() => {
    MockEventSource.instances = [];
    vi.stubGlobal('EventSource', MockEventSource);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should connect to SSE endpoint', () => {
    renderHook(() => useSSE({ url: '/api/stream' }));

    expect(MockEventSource.instances).toHaveLength(1);
    expect(MockEventSource.instances[0].url).toBe('/api/stream');
  });

  it('should update isConnected on open', async () => {
    const { result } = renderHook(() => useSSE({ url: '/api/stream' }));

    expect(result.current.isConnected).toBe(false);

    act(() => {
      MockEventSource.instances[0].simulateOpen();
    });

    expect(result.current.isConnected).toBe(true);
  });

  it('should call onMessage with parsed data', async () => {
    const onMessage = vi.fn();
    renderHook(() => useSSE({ url: '/api/stream', onMessage }));

    act(() => {
      MockEventSource.instances[0].simulateOpen();
      MockEventSource.instances[0].simulateMessage({ type: 'test', data: 'hello' });
    });

    expect(onMessage).toHaveBeenCalledWith({ type: 'test', data: 'hello' });
  });

  it('should reconnect on error', async () => {
    vi.useFakeTimers();

    renderHook(() => useSSE({ url: '/api/stream', reconnectInterval: 1000 }));

    act(() => {
      MockEventSource.instances[0].simulateError();
    });

    expect(MockEventSource.instances).toHaveLength(1);

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(MockEventSource.instances).toHaveLength(2);

    vi.useRealTimers();
  });

  it('should cleanup on unmount', () => {
    const { unmount } = renderHook(() => useSSE({ url: '/api/stream' }));

    const closeCall = MockEventSource.instances[0].close;

    unmount();

    expect(closeCall).toHaveBeenCalled();
  });
});
```

### Pusher Hook 테스트

```typescript
// hooks/__tests__/use-pusher.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePusher } from '../use-pusher';

// Pusher mock
const mockChannel = {
  bind: vi.fn(),
  unbind: vi.fn(),
};

const mockPusher = {
  subscribe: vi.fn(() => mockChannel),
  unsubscribe: vi.fn(),
};

vi.mock('@/lib/pusher/client', () => ({
  getPusherClient: () => mockPusher,
}));

describe('usePusher', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should subscribe to channel on mount', () => {
    renderHook(() =>
      usePusher({
        channel: 'test-channel',
        event: 'test-event',
        onEvent: vi.fn(),
      })
    );

    expect(mockPusher.subscribe).toHaveBeenCalledWith('test-channel');
    expect(mockChannel.bind).toHaveBeenCalledWith('test-event', expect.any(Function));
  });

  it('should call onEvent when event received', () => {
    const onEvent = vi.fn();
    renderHook(() =>
      usePusher({
        channel: 'test-channel',
        event: 'test-event',
        onEvent,
      })
    );

    // 이벤트 핸들러 가져오기
    const boundHandler = mockChannel.bind.mock.calls[0][1];

    // 이벤트 시뮬레이션
    act(() => {
      boundHandler({ message: 'hello' });
    });

    expect(onEvent).toHaveBeenCalledWith({ message: 'hello' });
  });

  it('should unsubscribe on unmount', () => {
    const { unmount } = renderHook(() =>
      usePusher({
        channel: 'test-channel',
        event: 'test-event',
        onEvent: vi.fn(),
      })
    );

    unmount();

    expect(mockChannel.unbind).toHaveBeenCalled();
    expect(mockPusher.unsubscribe).toHaveBeenCalledWith('test-channel');
  });
});
```

### WebSocket Hook 테스트

```typescript
// hooks/__tests__/use-websocket.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useWebSocket } from '../use-websocket';

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  static OPEN = 1;

  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((error: Event) => void) | null = null;
  readyState = 0;

  constructor(public url: string) {
    MockWebSocket.instances.push(this);
  }

  send = vi.fn();
  close = vi.fn();

  simulateOpen() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.();
  }

  simulateMessage(data: unknown) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }
}

describe('useWebSocket', () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.stubGlobal('WebSocket', MockWebSocket);
  });

  it('should send message when connected', () => {
    const { result } = renderHook(() =>
      useWebSocket({ url: 'ws://localhost/ws' })
    );

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    act(() => {
      result.current.send({ type: 'message', content: 'hello' });
    });

    expect(MockWebSocket.instances[0].send).toHaveBeenCalledWith(
      JSON.stringify({ type: 'message', content: 'hello' })
    );
  });

  it('should handle incoming messages', () => {
    const onMessage = vi.fn();
    renderHook(() =>
      useWebSocket({ url: 'ws://localhost/ws', onMessage })
    );

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
      MockWebSocket.instances[0].simulateMessage({ type: 'reply', data: 'world' });
    });

    expect(onMessage).toHaveBeenCalledWith({ type: 'reply', data: 'world' });
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 메모리 누수 - 정리 누락

```typescript
// ❌ Bad: interval/listener cleanup 누락
function useSSE(url: string) {
  useEffect(() => {
    const eventSource = new EventSource(url);
    eventSource.onmessage = (e) => console.log(e.data);
    // cleanup 없음!
  }, [url]);
}

// ✅ Good: 적절한 cleanup
function useSSE(url: string) {
  useEffect(() => {
    const eventSource = new EventSource(url);
    eventSource.onmessage = (e) => console.log(e.data);

    return () => {
      eventSource.close();  // cleanup!
    };
  }, [url]);
}
```

### 2. 무한 재연결 루프

```typescript
// ❌ Bad: 재연결 제한 없음
eventSource.onerror = () => {
  setTimeout(() => connect(), 1000);  // 무한 재연결!
};

// ✅ Good: 재연결 횟수 제한
const maxRetries = 5;
let retries = 0;

eventSource.onerror = () => {
  if (retries >= maxRetries) {
    console.error('Max retries reached');
    return;
  }
  retries++;
  setTimeout(() => connect(), 1000 * Math.pow(2, retries));  // 지수 백오프
};
```

### 3. 인증 없는 실시간 연결

```typescript
// ❌ Bad: 인증 없음
export async function GET(request: Request) {
  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  });
}

// ✅ Good: 인증 확인
export async function GET(request: Request) {
  const session = await auth();
  if (!session) {
    return new Response('Unauthorized', { status: 401 });
  }

  // ... stream logic
}
```

### 4. 콜백 의존성 무한 루프

```typescript
// ❌ Bad: onEvent가 매 렌더마다 새로 생성
usePusher({
  channel: 'chat',
  event: 'message',
  onEvent: (data) => setMessages((prev) => [...prev, data]),  // 무한 루프!
});

// ✅ Good: useCallback 또는 ref로 안정화
const handleEvent = useCallback((data: Message) => {
  setMessages((prev) => [...prev, data]);
}, []);

usePusher({
  channel: 'chat',
  event: 'message',
  onEvent: handleEvent,
});
```

---

## 에러 처리

### 연결 상태 관리

```typescript
// lib/realtime/connection-manager.ts
export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

export class ConnectionError extends Error {
  constructor(
    message: string,
    public code: ConnectionErrorCode,
    public retryable = true
  ) {
    super(message);
    this.name = 'ConnectionError';
  }
}

export type ConnectionErrorCode =
  | 'AUTH_FAILED'
  | 'NETWORK_ERROR'
  | 'SERVER_ERROR'
  | 'MAX_RETRIES_EXCEEDED';
```

### SSE 에러 핸들링

```typescript
export async function GET(request: Request) {
  const session = await auth();
  if (!session) {
    return new Response('Unauthorized', { status: 401 });
  }

  let isClosed = false;
  let heartbeat: NodeJS.Timeout | null = null;

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();

      const sendEvent = (data: unknown) => {
        if (isClosed) return;
        try {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
        } catch (error) {
          console.error('[SSE] Failed to send:', error);
          cleanup();
        }
      };

      const cleanup = () => {
        isClosed = true;
        if (heartbeat) clearInterval(heartbeat);
        try {
          controller.close();
        } catch {
          // Already closed
        }
      };

      // Heartbeat
      heartbeat = setInterval(() => {
        sendEvent({ type: 'heartbeat', timestamp: Date.now() });
      }, 30000);

      // Cleanup on client disconnect
      request.signal.addEventListener('abort', cleanup);
    },
    cancel() {
      isClosed = true;
      if (heartbeat) clearInterval(heartbeat);
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

---

## 성능 고려사항

### 채널 기반 브로드캐스트

```typescript
// Pusher 채널 분리로 불필요한 메시지 방지
// 모든 사용자에게 전송 X → 관련 채널만 구독

// 유저별 개인 채널
`private-user-${userId}`

// 채팅방별 채널
`presence-room-${roomId}`

// 전체 공지용 채널
`public-announcements`
```

### 메시지 배치 처리

```typescript
// 고빈도 업데이트 배치 처리
function useBatchedUpdates<T>(onBatch: (items: T[]) => void, delay = 100) {
  const bufferRef = useRef<T[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const addItem = useCallback((item: T) => {
    bufferRef.current.push(item);

    if (!timerRef.current) {
      timerRef.current = setTimeout(() => {
        onBatch([...bufferRef.current]);
        bufferRef.current = [];
        timerRef.current = null;
      }, delay);
    }
  }, [onBatch, delay]);

  return addItem;
}
```

### 연결 풀링

```typescript
// Pusher 클라이언트 싱글톤
let pusherClient: PusherClient | null = null;

export function getPusherClient() {
  if (!pusherClient) {
    pusherClient = new PusherClient(process.env.NEXT_PUBLIC_PUSHER_KEY!, {
      cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER!,
      // 연결 최적화
      enabledTransports: ['ws', 'wss'],
    });
  }
  return pusherClient;
}
```

---

## 보안 고려사항

### 채널 인증

```typescript
// app/api/pusher/auth/route.ts
export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const formData = await request.formData();
  const socketId = formData.get('socket_id') as string;
  const channel = formData.get('channel_name') as string;

  // 채널별 권한 검증
  if (channel.startsWith('private-')) {
    const userId = channel.replace('private-user-', '');
    if (userId !== session.user.id) {
      return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
    }
  }

  if (channel.startsWith('presence-room-')) {
    const roomId = channel.replace('presence-room-', '');
    const hasAccess = await checkRoomAccess(session.user.id, roomId);
    if (!hasAccess) {
      return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
    }
  }

  const authResponse = pusher.authorizeChannel(socketId, channel, {
    user_id: session.user.id,
    user_info: { name: session.user.name },
  });

  return NextResponse.json(authResponse);
}
```

### 메시지 검증

```typescript
// 서버에서 메시지 검증 후 브로드캐스트
const messageSchema = z.object({
  content: z.string().min(1).max(1000),
  channelId: z.string().uuid(),
});

export const sendMessageAction = authActionClient
  .schema(messageSchema)
  .action(async ({ parsedInput, ctx }) => {
    // XSS 방지
    const sanitizedContent = DOMPurify.sanitize(parsedInput.content);

    // 채널 접근 권한 확인
    const hasAccess = await checkChannelAccess(ctx.user.id, parsedInput.channelId);
    if (!hasAccess) {
      throw new ActionError('권한이 없습니다', 'FORBIDDEN');
    }

    await pusher.trigger(`channel-${parsedInput.channelId}`, 'new-message', {
      content: sanitizedContent,
      user: { id: ctx.user.id, name: ctx.user.name },
    });
  });
```

### Rate Limiting

```typescript
// 메시지 전송 rate limiting
const messageRateLimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(30, '1 m'),  // 분당 30개
});

export const sendMessageAction = authActionClient
  .schema(messageSchema)
  .action(async ({ parsedInput, ctx }) => {
    const { success } = await messageRateLimit.limit(`msg:${ctx.user.id}`);
    if (!success) {
      throw new ActionError('메시지를 너무 빠르게 보내고 있습니다', 'RATE_LIMITED');
    }

    // ... send message
  });
```

---

## References

- `_references/STATE-PATTERN.md`
- `_references/TEST-PATTERN.md`


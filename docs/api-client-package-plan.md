# 前端 api-client 包（设计）

## 目标
把 `bookmark-manager-web/src/api/` 抽出独立 npm 包，跨项目复用（CLI、桌面端、移动端）。

## 现状
- `src/api/client.ts` - 通用 client（useApiQuery + useApiMutation）
- `src/api/bookmarks.ts` - 书签 hooks
- `src/api/tags.ts` - 标签 hooks
- `src/api/ai.ts` - AI hooks
- 1 个 web 项目作为唯一消费者

## 设计：monorepo 拆分

```
bookmark-manager-workspace/        # 新 monorepo
├── pnpm-workspace.yaml
├── packages/
│   ├── api-client/               # 独立 npm 包
│   │   ├── package.json          # "@bookmark/api-client"
│   │   ├── src/
│   │   │   ├── client.ts
│   │   │   ├── hooks/
│   │   │   │   ├── bookmarks.ts
│   │   │   │   ├── tags.ts
│   │   │   │   └── ai.ts
│   │   │   ├── types.ts
│   │   │   └── index.ts
│   │   └── tsconfig.json
│   └── web/                       # 原 web 项目
│       ├── package.json          # 引用 "@bookmark/api-client": "workspace:*"
│       └── src/
└── README.md
```

## API 客户端 API 设计

```typescript
// packages/api-client/src/hooks/bookmarks.ts
export function useBookmarks(params?: {
  limit?: number;
  offset?: number;
  tag?: string;
  category?: string;
  q?: string;
}) {
  return useApiQuery(['bookmarks', params], '/v1/bookmarks', { params });
}

export function useAddBookmark() {
  return useApiMutation<Bookmark, AddBookmarkInput>(
    '/v1/bookmark',
    'POST',
    { invalidateKeys: [['bookmarks'], ['stats']] }
  );
}

export function useDeleteBookmark() {
  return useApiMutation<{ ok: boolean }, { id: string }>(
    '/v1/bookmark/delete',
    'POST',
    { invalidateKeys: [['bookmarks']] }
  );
}
```

## 工具

**pnpm workspaces**（推荐）
```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
```

**Turborepo**（可选，加速构建）
```json
// turbo.json
{
  "tasks": {
    "build": { "outputs": ["dist/**"] },
    "test": { "dependsOn": ["build"] }
  }
}
```

## 收益

1. **跨项目复用**：CLI（`@bookmark/cli`）、桌面端（Electron）、移动端（React Native）都用同一套 API
2. **独立版本管理**：`@bookmark/api-client` 可以单独发版
3. **类型安全**：TypeScript 类型从 server Pydantic schema 自动生成（可选）

## 工时

- L2-design（本文档）：已完成
- L2-impl：
  - 建 pnpm-workspace：1 小时
  - 抽 `client.ts` → api-client 包：2 小时
  - 抽 `bookmarks.ts` / `tags.ts` / `ai.ts`：2 小时
  - web 项目改引用 workspace 包：1 小时
  - 测试：1 小时
- 合计：~7 小时（1 天）

## 优先级

**低**。当前只有 1 个 web 消费者，抽包需要：
- 把现有 web 拆 2 个 package
- CI 配置改
- 文档重写

短期收益不明显，**建议在确实要做 CLI / 桌面端时再做**。
EOF
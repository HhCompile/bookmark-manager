# TODO: DeepSeek API Key 前端输入功能

> 状态：**草案 / 待开发**
> 创建：2026-07-08
> 来源：本会话用户决策（替代当前 admin/.env 全局 DEEPSEEK_API_KEY 机制）

---

## 🎯 目标

每个登录用户**自己填入**自己的 DeepSeek API key，单独存储，**前端加密 + 后端加密双重保护**，随登录身份走。

## 📋 当前痛点

- admin/.env 中 DEEPSEEK_API_KEY_ENCRYPTED 是**全局**的
- 所有用户共用一个 key
- key 重置需要改环境变量 + 重新部署
- 单一 key 用量配额共享，无法限速单个滥用

## 🏗️ 设计草案

### 数据流

```
用户设置页
  ↓ 输入明文 API key
前端 (Web Crypto API)
  ↓ AES-GCM 加密（user password PBKDF2 派生 key + per-user salt）
EncryptedBlob { ciphertext, nonce, salt, algorithm }
  ↓ POST /v1/user/deepseek-key
后端 (admin)
  ↓ 再加密一层（server master key from settings）
ReEncryptedBlob (存 SQLite users.encrypted_deepseek_key)
```

### 数据库

users 表新增列：
- `encrypted_deepseek_key BLOB` — 后端二次加密的密文
- `key_algorithm VARCHAR` — 算法标识
- `key_iv VARCHAR` — IV
- `key_updated_at TIMESTAMP`

### API 契约

| Method | Endpoint | 用途 |
|---|---|---|
| POST | `/v1/user/deepseek-key` | 用户提交 key（前密文） |
| GET | `/v1/user/deepseek-key` | 用户查看是否已设（仅返回 masked 状态） |
| DELETE | `/v1/user/deepseek-key` | 用户清除 key |
| POST | `/v1/ai/suggest` | 调 AI（如果用户有 key 用其，否则用 server default） |

### 前端 UI

设置页（已有 SettingsPage？）→ 新增 tab「AI 服务」：
- 输入框：DeepSeek API key
- 「测试连接」按钮 → POST 一句简单 prompt 验证
- 「清除」按钮
- 提示：key 仅保存在服务端加密 blob，logout 后无法恢复

### 加密细节

**前端**：
- 算法：AES-GCM 256
- 派生：从 user password 派生（PBKDF2 / Argon2）— 但密码不会每次请求都带，前端先 derive 然后存 localStorage session key
- IV 每次随机 12 字节

**后端**：
- 算法：AES-GCM 256，与前端一致但 key 不同
- 服务端 master key 从 server config 读（不是 user password）

**双层加密目的**：
- 即使 SQLite 泄露，攻击者需要：(server master key) 才能解开
- 即使 client dev tools 被 XSS，前端密文需用户 password 才能解开

## ⚠️ 待决定

1. **前端密码派生**：是否复用登录密码？
   - 优点：用户不用记额外密码
   - 缺点：每次登录都要重新输入密文丢失则需重新填 key
2. **Server default fallback**：没有 user key 是否回落到 admin/.env 全局？
   - 优点：onboarding 新用户有默认体验
   - 缺点：单一 key 用量配额共享问题仍在
3. **Multi-provider**：是否同接口支持 OpenAI / Anthropic / Gemini？
   - 这次先只 DeepSeek，结构上预留 provider 字段
4. **历史迁移**：现有 admin/.env DEEPSEEK_API_KEY_ENCRYPTED 怎么办？
   - 第一阶段可保留作"系统级默认 key"
   - 第二阶段用户填了之后默认被覆盖（不再回退？）

## 📅 工作拆分

1. 后端：`app_v2/routers/auth.py` 加 4 个 user key 路由
2. 后端：`app/services/ai_key_service.py` 新文件，加密 / 解密
3. 后端：`scripts/migrate_json_to_sqlite.py` 加 users.encrypted_deepseek_key 列
4. 前端：`src/components/settings/AIKeySettings.tsx` 新组件
5. 前端：`src/api/userKey.ts` 新 API 客户端
6. 前端：`src/pages/settings/SettingsPage.tsx` 加 tab
7. 前端：crypto helper `src/utils/webCrypto.ts`
8. 测试：前后端各加 E2E 测试

## 🔗 相关文件

- `app/api/routes_ai.py` — 现有 V1 AI 路由参考
- `app/utils/auth.py` — V1 auth 模块参考
- `app_v2/routers/ai.py` — V2 AI 路由（实际调用 key 的地方）
- `src/contexts/AuthContext.tsx` — 前端已有 Auth 状态管理
- `src/components/auth/UserMenu.tsx` — 用户菜单

# 私密空间加密方案（设计）

> [[Private Vault Pending]] 完整实现

## 目标
私密书签的端到端加密：服务端永远看不到明文，只有用户自己能解密。

## 现状
- 已有 UI 外壳（`PrivateVault` 组件）
- 服务端只存明文到 `bookmarks.json`
- 没有加密逻辑

## 威胁模型

| 攻击 | 是否保护 |
|------|---------|
| 服务端数据库泄漏 | ✅ 加密后泄漏得到密文 |
| 服务端管理员查看 | ✅ 不知道主密码 |
| 中间人攻击 | ✅ HTTPS 保护 |
| 客户端恶意软件 | ❌ 主密码在内存中 |
| 暴力破解主密码 | ⚠️ 取决于密码强度（用 Argon2） |

## 设计：客户端加密 + 主密码

### 1. 主密码派生密钥

```typescript
// 前端：web 端用 Web Crypto API
async function deriveKey(masterPassword: string, salt: Uint8Array): Promise<CryptoKey> {
  const encoder = new TextEncoder();
  const baseKey = await crypto.subtle.importKey(
    "raw", encoder.encode(masterPassword), "PBKDF2", false, ["deriveKey"]
  );
  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt,
      iterations: 600_000,  // 2024 OWASP 推荐
      hash: "SHA-256",
    },
    baseKey,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"]
  );
}
```

### 2. 加密书签

```typescript
async function encryptBookmark(bm: Bookmark, key: CryptoKey): Promise<string> {
  const iv = crypto.getRandomValues(new Uint8Array(12));  // AES-GCM 96-bit
  const plaintext = JSON.stringify({
    url: bm.url, title: bm.title, description: bm.description,
    tags: bm.tags, category: bm.category, folder_path: bm.folder_path,
  });
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    new TextEncoder().encode(plaintext)
  );
  // 存：salt + iv + ciphertext (base64 编码)
  return {
    salt: btoa(String.fromCharCode(...SALT)),
    iv: btoa(String.fromCharCode(...iv)),
    ciphertext: btoa(String.fromCharCode(...new Uint8Array(ciphertext))),
  };
}
```

### 3. 服务端存储

在 `bookmarks` 表加字段：
```sql
ALTER TABLE bookmarks ADD COLUMN is_private INTEGER DEFAULT 0;
ALTER TABLE bookmarks ADD COLUMN encrypted_payload TEXT;  -- JSON: {salt, iv, ciphertext}
```

私密书签的 `url` / `title` 等字段在数据库中**留空**（或存哈希指纹），真正的数据在 `encrypted_payload`。

### 4. 解密流程

```
用户登录 → 输入主密码 → 派生 AES key
↓ 加载私密书签 → AES-GCM 解密 → 显示明文
```

### 5. API 设计

```
GET  /v1/vault/bookmarks        → 返回 encrypted_payload 列表（不含明文）
POST /v1/vault/bookmarks        → 上传加密 payload
PUT  /v1/vault/bookmarks/:id    → 替换加密 payload
DELETE /v1/vault/bookmarks/:id
POST /v1/vault/decrypt          → 客户端先调这拿 salt，派生 key，再解本地

（注意：服务端永远不解密，key 只在客户端）
```

## 关键决策

1. **AES-256-GCM**：业界标准，认证加密（防篡改）
2. **PBKDF2 + 600k 迭代**：防暴力破解（OWASP 2024 推荐）
3. **per-bookmark IV**：每次加密用新随机 IV，相同书签不同密文
4. **服务端零知识**：服务端代码不应该有解密函数（万一泄漏也不暴露）
5. **主密码不存**：服务端永远不知道主密码

## 边界情况

| 情况 | 处理 |
|------|------|
| 用户忘记主密码 | **无法恢复**（设计如此） |
| 浏览器多设备同步 | 用同一主密码分别派生，salt 存在服务端 |
| 客户端不支持 Web Crypto | 降级提示用户升级浏览器 |
| 主密码弱 | 强制要求 12+ 字符 + 强度计 |

## 工时

- L3-design（本文档）：已完成
- L3-impl：
  - 客户端加密库：`packages/crypto/`：1 周
  - 服务端 vault 端点：1 周
  - UI 改造（PrivateVault 组件用解密流程）：3 天
  - 测试 + 安全审计：1 周
  - 文档 + 隐私政策：2 天
- 合计：~1 个月

## 优先级

**中高**。这是 [[Private Vault Pending]] 的核心缺口，但工作量大。
- 短期可以做：salt 派生 + 加密函数原型（2-3 天）
- 完整版本：1 个月

## 安全审计清单

- [ ] 主密码不存任何形式（明文、哈希、加密）
- [ ] AES-GCM IV 每次唯一
- [ ] PBKDF2 迭代 ≥ 600k
- [ ] 前端代码不打印 / 上报主密码
- [ ] 服务端日志不含书签明文
- [ ] 浏览器退出时清空内存中的 key
EOF
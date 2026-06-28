---
name: feature-dev
description: 书签管理器功能开发完整流程 - 从需求到发布
type: flow
---

# 功能开发流程

Bookmark Manager 项目标准功能开发工作流。

## 流程说明

本流程涵盖从前端、后端到测试的完整开发周期，确保前后端 API 对齐。

## 流程图（D2 格式）

```d2
direction: down

# 样式定义
classes: {
  startEnd: {
    shape: oval
    style.fill: "#e1f5fe"
    style.stroke: "#0288d1"
    style.stroke-width: 2
  }
  
  process: {
    shape: rectangle
    style.fill: "#fff8e1"
    style.stroke: "#ffa000"
  }
  
  decision: {
    shape: diamond
    style.fill: "#f3e5f5"
    style.stroke: "#7b1fa2"
  }
  
  backend: {
    shape: rectangle
    style.fill: "#e8f5e9"
    style.stroke: "#388e3c"
  }
  
  frontend: {
    shape: rectangle
    style.fill: "#e3f2fd"
    style.stroke: "#1976d2"
  }
}

# 节点定义
BEGIN: {
  class: startEnd
  label: |md
    **开始新功能开发**
    明确需求和技术方案
  |
}

DESIGN: {
  class: process
  label: |md
    **设计阶段**
    
    1. 更新 API 文档 (openapi.yaml)
    2. 设计数据模型
    3. 定义接口契约
  |
}

API_REVIEW: {
  class: decision
  label: |md
    **API 评审**
    前后端确认？
  |
}

BACKEND_DEV: {
  class: backend
  label: |md
    **后端开发**
    
    1. Model 层更新
    2. Service 层实现
    3. API 端点开发
    4. 本地测试
  |
}

FRONTEND_DEV: {
  class: frontend
  label: |md
    **前端开发**
    
    1. API 客户端更新
    2. 类型定义 (types/)
    3. 组件开发
    4. 页面集成
  |
}

API_ALIGN: {
  class: decision
  label: |md
    **API 联调**
    接口对齐？
  |
}

TEST: {
  class: process
  label: |md
    **测试阶段**
    
    - 单元测试
    - 集成测试
    - Chrome 扩展测试
  |
}

TEST_PASS: {
  class: decision
  label: |md
    **测试通过？**
  |
}

BUG_FIX: {
  class: process
  style.fill: "#ffebee"
  style.stroke: "#d32f2f"
  label: |md
    **修复问题**
    根据测试反馈修复
  |
}

DEPLOY: {
  class: process
  label: |md
    **部署发布**
    
    - 构建前端
    - 部署后端
    - 更新文档
  |
}

END: {
  class: startEnd
  label: |md
    **功能上线**
  |
}

# 连接
BEGIN -> DESIGN
DESIGN -> API_REVIEW

API_REVIEW -> BACKEND_DEV: 确认通过
API_REVIEW -> DESIGN: 需修改 (循环)

BACKEND_DEV -> API_ALIGN
FRONTEND_DEV -> API_ALIGN

API_ALIGN -> TEST: 对齐成功
API_ALIGN -> BACKEND_DEV: 后端需修改
API_ALIGN -> FRONTEND_DEV: 前端需修改

TEST -> TEST_PASS
TEST_PASS -> DEPLOY: 是
TEST_PASS -> BUG_FIX: 否

BUG_FIX -> TEST

DEPLOY -> END
```

## 各阶段详细说明

### 1. 设计阶段

- 更新 `bookmark-manager-admin/openapi.yaml`
- 确认 API 路径、请求/响应格式
- 前后端协商确认

### 2. 后端开发 (Python/Flask)

目录结构：
```
app/
├── models/         # 数据模型
├── services/       # 业务逻辑
├── controllers/    # 控制器
└── api/           # API 路由
```

编码规范：
- 文件使用 snake_case
- 类使用 PascalCase
- 方法和变量使用 snake_case
- 注释使用中文

### 3. 前端开发 (React/TypeScript)

目录结构：
```
src/
├── api/           # API 客户端
├── types/         # TypeScript 类型
├── components/    # 组件
└── pages/         # 页面
```

编码规范：
- 组件使用 PascalCase
- Hooks 使用 camelCase 以 use 开头
- 工具函数使用 camelCase
- 优先使用 `@/` 绝对导入

### 4. API 联调

使用 curl 或 Postman 测试：
```bash
# 健康检查
curl http://127.0.0.1:9001/v1/health

# 测试新 API
curl -X POST http://127.0.0.1:9001/v1/bookmark \
  -H "Content-Type: application/json" \
  -d '{"url": "...", "title": "..."}'
```

### 5. 测试阶段

前端测试：
```bash
cd bookmark-manager-web
pnpm test
pnpm typecheck
pnpm lint
```

后端测试：
```bash
cd bookmark-manager-admin
python -m pytest  # 如有测试
```

### 6. 部署

前端构建：
```bash
cd bookmark-manager-web
pnpm build
```

后端部署：
```bash
cd bookmark-manager-admin
gunicorn -w 4 -b 0.0.0.0:9001 run:app
```

## 关键检查点

| 阶段 | 检查项 | 负责人 |
|------|--------|--------|
| API 评审 | openapi.yaml 更新 | 前后端共同 |
| 后端完成 | 单元测试通过 | 后端开发 |
| 前端完成 | Lint + TypeCheck 通过 | 前端开发 |
| 联调完成 | API 对齐文档 | 双方确认 |
| 发布前 | 全量功能测试 | QA/开发 |

## 使用方式

在 Kimi CLI 中执行：
```
/flow:feature-dev
```

AI 将按照流程图逐步引导你完成功能开发。

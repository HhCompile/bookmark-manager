---
name: code-review
description: 书签管理器项目代码审查工作流 - 确保代码质量和一致性
type: flow
---

# 代码审查流程

针对 Bookmark Manager 项目的代码审查标准流程。

## 审查范围

- 前端：React + TypeScript + Vite
- 后端：Flask + Python
- 数据库：JSON 文件存储

## 审查清单

1. **代码风格**
   - 前端：ESLint + Prettier 规则
   - 后端：PEP 8 + 中文注释

2. **安全**
   - XSS 防护
   - 文件上传验证
   - CORS 配置

3. **性能**
   - 组件懒加载
   - API 响应优化

## 流程图

```d2
direction: down

BEGIN: {
  shape: oval
  label: |md
    **开始审查**
    获取 PR/MR 信息
  |
}

ANALYZE: {
  shape: rectangle
  label: |md
    **分析变更**
    1. 列出所有修改文件
    2. 识别前端/后端变更
    3. 检查 API 变更是否同步
  |
}

CHECK_STYLE: {
  shape: diamond
  label: |md
    **代码风格**
    符合规范？
  |
}

CHECK_SECURITY: {
  shape: diamond
  label: |md
    **安全检查**
    无安全隐患？
  |
}

CHECK_API: {
  shape: diamond
  label: |md
    **API 对齐**
    前后端一致？
}

ISSUES: {
  shape: rectangle
  style.fill: "#ffcccc"
  label: |md
    **记录问题**
    - 代码风格问题
    - 安全隐患
    - API 不一致
    - 缺少测试
  |
}

REPORT: {
  shape: rectangle
  style.fill: "#ccffcc"
  label: |md
    **生成报告**
    - 审查总结
    - 建议改进
    - 通过/拒绝决定
  |
}

END: {
  shape: oval
  label: |md
    **审查完成**
  |
}

BEGIN -> ANALYZE
ANALYZE -> CHECK_STYLE

CHECK_STYLE -> CHECK_SECURITY: 是
CHECK_STYLE -> ISSUES: 否

CHECK_SECURITY -> CHECK_API: 是
CHECK_SECURITY -> ISSUES: 否

CHECK_API -> REPORT: 是
CHECK_API -> ISSUES: 否

ISSUES -> ANALYZE: 修复后重新审查

REPORT -> END
```

## 审查标准

### 前端代码

| 检查项 | 标准 |
|--------|------|
| 类型安全 | 无 `any` 类型 |
| 组件命名 | PascalCase |
| Hook 命名 | 以 `use` 开头 |
| 导入顺序 | React → 第三方 → `@/` → 相对路径 |

### 后端代码

| 检查项 | 标准 |
|--------|------|
| 文件命名 | snake_case |
| 编码声明 | `# -*- coding: utf-8 -*-` |
| 注释语言 | 中文 |
| 导入顺序 | 标准库 → 第三方 → 本地模块 |

## 输出格式

审查报告应包含：

1. **变更摘要** - 修改的文件和功能
2. **问题列表** - 按严重程度分类
3. **建议** - 具体改进建议
4. **决定** - APPROVE / REQUEST_CHANGES / COMMENT

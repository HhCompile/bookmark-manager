---
name: ui-workflow
description: UI/UX 设计完整工作流 - 从需求分析到设计交付的标准化流程
type: flow
---

# UI 设计工作流

Bookmark Manager 项目 UI 设计的标准化流程。

## 适用场景

- 新功能界面设计
- 现有界面优化
- 设计系统维护
- 设计审查

## 流程图

```d2
direction: down

# 样式定义
classes: {
  startEnd: {
    shape: oval
    style.fill: "#e3f2fd"
    style.stroke: "#1976d2"
  }
  
  process: {
    shape: rectangle
    style.fill: "#f5f5f5"
    style.stroke: "#616161"
  }
  
  decision: {
    shape: diamond
    style.fill: "#fff3e0"
    style.stroke: "#f57c00"
  }
  
  design: {
    shape: rectangle
    style.fill: "#fce4ec"
    style.stroke: "#c2185b"
  }
  
  review: {
    shape: rectangle
    style.fill: "#e8f5e9"
    style.stroke: "#388e3c"
  }
  
  dev: {
    shape: rectangle
    style.fill: "#e1f5fe"
    style.stroke: "#0288d1"
  }
}

# 流程节点
BEGIN: {
  class: startEnd
  label: |md
    **开始**
    接收设计需求
  |
}

ANALYZE: {
  class: process
  label: |md
    **需求分析**
    1. 理解业务目标
    2. 分析用户场景
    3. 确定功能范围
    4. 竞品参考研究
  |
}

WIREFRAME: {
  class: design
  label: |md
    **线框图**
    - 低保真原型
    - 信息架构
    - 页面流程
    - 布局规划
  |
}

WIREFRAME_REVIEW: {
  class: decision
  label: |md
    **线框评审**
    结构合理？
  |
}

VISUAL: {
  class: design
  label: |md
    **视觉设计**
    - 高保真设计稿
    - 设计系统应用
    - 色彩、字体、图标
    - 交互动效定义
  |
}

A11Y_CHECK: {
  class: process
  label: |md
    **可访问性检查**
    - 对比度检测
    - 键盘导航
    - ARIA 标签
  |
}

RESPONSIVE: {
  class: design
  label: |md
    **响应式设计**
    - 移动端适配
    - 断点设计
    - 布局调整
  |
}

DESIGN_REVIEW: {
  class: review
  label: |md
    **设计评审**
    - 视觉一致性
    - 交互完整性
    - 设计规范符合
  |
}

APPROVED: {
  class: decision
  label: |md
    **评审通过？**
  |
}

ITERATE: {
  class: design
  style.fill: "#ffebee"
  style.stroke: "#d32f2f"
  label: |md
    **设计迭代**
    根据反馈修改
  |
}

HANDOFF: {
  class: dev
  label: |md
    **设计交付**
    - 标注说明
    - 切图资源
    - 交互说明
    - Token 映射
  |
}

DEV_REVIEW: {
  class: dev
  label: |md
    **开发审查**
    - 技术可行性
    - 实现细节确认
    - 工期评估
  |
}

IMPLEMENT: {
  class: dev
  label: |md
    **开发实现**
    - 前端编码
    - 组件开发
    - 响应式适配
  |
}

QA: {
  class: review
  label: |md
    **设计走查**
    - 视觉还原度
    - 交互一致性
    - 响应式测试
  |
}

QA_PASS: {
  class: decision
  label: |md
    **走查通过？**
  |
}

FIX: {
  class: dev
  style.fill: "#ffebee"
  style.stroke: "#d32f2f"
  label: |md
    **问题修复**
    视觉还原问题
  |
}

DONE: {
  class: startEnd
  label: |md
    **完成上线**
  |
}

# 流程连接
BEGIN -> ANALYZE
ANALYZE -> WIREFRAME

WIREFRAME -> WIREFRAME_REVIEW
WIREFRAME_REVIEW -> VISUAL: 是
WIREFRAME_REVIEW -> WIREFRAME: 否，调整

VISUAL -> A11Y_CHECK
A11Y_CHECK -> RESPONSIVE
RESPONSIVE -> DESIGN_REVIEW

DESIGN_REVIEW -> APPROVED
APPROVED -> HANDOFF: 是
APPROVED -> ITERATE: 否
ITERATE -> VISUAL

HANDOFF -> DEV_REVIEW
DEV_REVIEW -> IMPLEMENT
IMPLEMENT -> QA

QA -> QA_PASS
QA_PASS -> DONE: 是
QA_PASS -> FIX: 否
FIX -> QA
```

## 各阶段详细说明

### 1. 需求分析

**输入**: PRD、用户故事、功能列表
**输出**: 需求理解文档、设计目标

**检查项**:
- [ ] 理解业务目标
- [ ] 明确目标用户
- [ ] 梳理用户场景
- [ ] 列出功能清单
- [ ] 收集竞品参考

### 2. 线框图 (Wireframe)

**工具**: Figma / Excalidraw
**重点**: 结构、流程、布局

**交付物**:
- 页面流程图
- 低保真原型
- 信息架构图

### 3. 视觉设计

**应用设计系统**:
- 颜色 Token: `bg-primary`, `text-foreground`
- 间距系统: `space-4`, `space-6`
- 圆角规范: `rounded-md`, `rounded-lg`
- 字体层级: `text-sm`, `text-base`, `text-xl`

**组件使用**:
```
Button - 主要/次要/描边/幽灵
Card - 内容容器
Input - 表单输入
Dialog - 模态框
Dropdown - 下拉菜单
```

### 4. 可访问性检查

**工具**: axe DevTools, WebAIM Contrast Checker

**检查清单**:
- [ ] 颜色对比度 ≥ 4.5:1
- [ ] 键盘可访问
- [ ] 焦点可见
- [ ] ARIA 标签完整
- [ ] 屏幕阅读器友好

### 5. 响应式设计

**断点设计**:
```
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: > 1024px
```

**适配策略**:
- 移动端优先
- 核心内容优先显示
- 触控目标 ≥ 44px
- 避免横向滚动

### 6. 设计评审

**评审维度**:

| 维度 | 检查点 |
|------|--------|
| 视觉 | 一致性、美观度、品牌契合 |
| 交互 | 易用性、反馈、流畅度 |
| 规范 | 设计系统符合度 |
| 可访问 | 包容性、键盘支持 |

### 7. 设计交付

**交付清单**:

1. **设计稿**
   - Figma 链接（开发者模式）
   - 标注：尺寸、间距、颜色
   - 多状态展示

2. **资源**
   - 图标（SVG 格式）
   - 图片（优化后）
   - 字体（如有自定义）

3. **文档**
   - 交互说明
   - 动画参数
   - 响应式断点
   - Token 映射表

### 8. 设计走查

**检查项**:
- [ ] 像素级还原
- [ ] 颜色正确
- [ ] 字体一致
- [ ] 间距准确
- [ ] 交互流畅
- [ ] 响应式正常
- [ ] 可访问性达标

**走查工具**:
- Figma Dev Mode
- Browser DevTools
- axe DevTools

---

## 设计评审模板

```markdown
## 设计评审: [功能名称]

### 评审信息
- **日期**: YYYY-MM-DD
- **设计师**: @name
- **参与者**: @dev @pm @qa

### 设计目标
[描述该设计解决的问题]

### 方案概述
[简述设计方案]

### 评审反馈

#### ✅ 通过项
- [反馈1]
- [反馈2]

#### 🔧 需修改
- [问题1]: [修改建议]
- [问题2]: [修改建议]

### 下一步
- [ ] [待办1]
- [ ] [待办2]

### 决策
- [ ] 通过，进入开发
- [ ] 需修改后复审
```

---

## 使用方式

在 Kimi CLI 中执行：
```
/flow:ui-workflow
```

AI 将按流程图逐步引导完成 UI 设计工作。

---

*版本: 1.0.0 | 适用项目: Bookmark Manager*

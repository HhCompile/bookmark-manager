---
name: ui-expert
description: UI/UX 设计专家 - 提供设计系统、组件设计、响应式布局、可访问性和设计-开发协作的专业指导
license: MIT
compatibility: 适用于 React + Tailwind CSS + shadcn/ui 技术栈的项目
metadata:
  version: 1.0.0
  author: Bookmark Manager Team
  tags: [ui, ux, design-system, accessibility, responsive]
---

# UI/UX 设计专家

为 Bookmark Manager 项目提供专业的用户界面和用户体验设计指导。

## 适用场景

- 设计新功能界面
- 审查现有 UI 设计
- 建立/维护设计系统
- 组件设计和复用
- 响应式布局优化
- 可访问性改进

## 技术栈

- **框架**: React 18 + TypeScript
- **样式**: Tailwind CSS 4.x
- **组件**: shadcn/ui + Radix UI
- **动画**: Motion (Framer Motion)
- **图标**: Lucide React

---

## 设计原则

### 1. 一致性 (Consistency)

```typescript
// ✅ 使用设计系统预设值
import { cn } from "@/lib/utils";

// 使用统一的间距、颜色、圆角
<button className={cn(
  "px-4 py-2 rounded-md",
  "bg-primary text-primary-foreground",
  "hover:bg-primary/90",
  "transition-colors"
)}>
  提交
</button>
```

### 2. 简洁性 (Simplicity)

- 每页只有一个主要行动点 (CTA)
- 减少视觉噪音
- 使用留白创造呼吸感

### 3. 反馈性 (Feedback)

```typescript
// 按钮状态反馈
<Button 
  disabled={isLoading}
  className="relative"
>
  {isLoading && (
    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  )}
  保存
</Button>
```

### 4. 可访问性 (Accessibility)

- 支持键盘导航
- 提供 ARIA 标签
- 确保足够的颜色对比度 (WCAG 4.5:1)

---

## 设计系统规范

### 色彩系统

| Token | 用途 | 示例 |
|-------|------|------|
| `bg-primary` | 主要按钮、强调 | 主题色 |
| `bg-secondary` | 次要按钮、背景 | 次要色 |
| `bg-muted` | 禁用、背景 | 灰色系 |
| `bg-destructive` | 危险操作 | 红色系 |
| `text-foreground` | 主要文字 | 深色 |
| `text-muted-foreground` | 次要文字 | 灰色 |

### 间距系统

基于 4px 网格系统：

| Token | 值 | 用途 |
|-------|-----|------|
| `space-1` | 4px | 紧凑间距 |
| `space-2` | 8px | 小间距 |
| `space-4` | 16px | 标准间距 |
| `space-6` | 24px | 大间距 |
| `space-8` | 32px | 章节间距 |

### 圆角系统

| Token | 值 | 用途 |
|-------|-----|------|
| `rounded-sm` | 2px | 标签、小元素 |
| `rounded-md` | 6px | 按钮、输入框 |
| `rounded-lg` | 8px | 卡片、面板 |
| `rounded-xl` | 12px | 大卡片、模态框 |

### 字体系统

| 样式 | 大小 | 字重 | 用途 |
|------|------|------|------|
| `text-xs` | 12px | normal | 标签、辅助文字 |
| `text-sm` | 14px | normal | 正文、按钮 |
| `text-base` | 16px | normal | 主要正文 |
| `text-lg` | 18px | medium | 小标题 |
| `text-xl` | 20px | semibold | 章节标题 |
| `text-2xl` | 24px | bold | 页面标题 |

---

## 组件设计规范

### 按钮 (Button)

```typescript
// 变体使用
<Button variant="default">主要</Button>     // 实心主色
<Button variant="secondary">次要</Button>   // 实心次要
<Button variant="outline">描边</Button>     // 描边样式
<Button variant="ghost">幽灵</Button>       // 无背景
<Button variant="link">链接</Button>        // 文字链接

// 尺寸
<Button size="sm">小</Button>      // 紧凑
<Button size="default">默认</Button> // 标准
<Button size="lg">大</Button>      // 突出
<Button size="icon">icon</Button>  // 图标按钮
```

### 卡片 (Card)

```typescript
<Card>
  <CardHeader>
    <CardTitle>标题</CardTitle>
    <CardDescription>描述文字</CardDescription>
  </CardHeader>
  <CardContent>
    {/* 内容 */}
  </CardContent>
  <CardFooter>
    {/* 操作按钮 */}
  </CardFooter>
</Card>
```

### 表单组件

```typescript
// 输入框
<Input 
  placeholder="请输入..."
  className="max-w-sm"
/>

// 带标签的输入框
<div className="grid w-full max-w-sm items-center gap-1.5">
  <Label htmlFor="email">邮箱</Label>
  <Input id="email" type="email" />
  <p className="text-sm text-muted-foreground">
    我们将不会分享您的邮箱
  </p>
</div>

// 选择框
<Select>
  <SelectTrigger className="w-[180px]">
    <SelectValue placeholder="选择分类" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="tech">技术</SelectItem>
    <SelectItem value="design">设计</SelectItem>
  </SelectContent>
</Select>
```

---

## 响应式设计

### 断点系统

```css
/* Tailwind 默认断点 */
sm: 640px   /* 手机横屏 */
md: 768px   /* 平板 */
lg: 1024px  /* 小桌面 */
xl: 1280px  /* 桌面 */
2xl: 1536px /* 大桌面 */
```

### 响应式模式

```typescript
// 网格布局
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>

// 弹性布局
<div className="flex flex-col md:flex-row gap-4">
  <Sidebar className="w-full md:w-64" />
  <MainContent className="flex-1" />
</div>

// 隐藏/显示
<MobileNav className="lg:hidden" />
<DesktopNav className="hidden lg:block" />
```

---

## 布局模式

### 页面布局

```typescript
// 标准页面结构
<div className="min-h-screen flex flex-col">
  <Header />
  <div className="flex-1 flex">
    <Sidebar className="w-64 hidden md:block" />
    <main className="flex-1 p-6">
      <PageHeader />
      <PageContent />
    </main>
  </div>
</div>
```

### 内容区域

```typescript
// 容器
<div className="container mx-auto px-4 sm:px-6 lg:px-8">
  {/* 内容 */}
</div>

// 最大宽度限制
<div className="max-w-3xl mx-auto">
  {/* 文章内容 */}
</div>
```

---

## 动画与过渡

### 基础过渡

```typescript
// 颜色过渡
<button className="transition-colors duration-200">

// 综合过渡
<div className="transition-all duration-300 ease-in-out">
```

### Motion 动画

```typescript
import { motion, AnimatePresence } from "motion/react";

// 入场动画
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  内容
</motion.div>

// 列表动画
<AnimatePresence>
  {items.map((item) => (
    <motion.div
      key={item.id}
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      layout
    >
      {item.content}
    </motion.div>
  ))}
</AnimatePresence>
```

---

## 可访问性检查清单

### 键盘导航

- [ ] 所有交互元素可通过 Tab 键访问
- [ ] 焦点状态清晰可见
- [ ] 支持 Enter/Space 激活按钮
- [ ] 模态框支持 ESC 关闭

### 屏幕阅读器

```typescript
// 提供 aria 标签
<button aria-label="关闭对话框">
  <XIcon />
</button>

// 描述状态
<span className="sr-only">加载中</span>
<div aria-live="polite" role="status">
  {message}
</div>
```

### 颜色对比

- 正文文字 vs 背景: 至少 4.5:1
- 大文字 (18px+) vs 背景: 至少 3:1
- 使用 [WebAIM 对比度检查器](https://webaim.org/resources/contrastchecker/)

---

## UI 走查指南 (UI Audit)

UI 走查是确保视觉还原度和用户体验的关键环节。以下是系统化的走查方法。

### 走查准备

**工具准备**:
- Chrome DevTools
- Figma Dev Mode
- Pixel Perfect 插件
- axe DevTools

**环境准备**:
- 测试数据：准备真实长度/内容的数据
- 多分辨率：测试 375px, 768px, 1440px
- 多浏览器：Chrome, Safari, Firefox

### 文字排印走查

#### 1. 文字换行问题

**常见问题**: 文字在不允许的地方换行

**检查场景**:
```
❌ 错误示例 - 英文单词被截断
按钮文字: "Cancel" → "Can-\ncel"

❌ 错误示例 - 数字被换行
日期: "2026-04-06" → "2026-\n04-06"

❌ 错误示例 - 专有名词被截断
"GitHub" → "Git-\nHub"
"YouTube" → "You-\nTube"

❌ 错误示例 - 操作按钮文字换行
[保存更改] → [保存\n更改]
```

**解决方案**:

```css
/* 方案1: 禁止文字换行 */
.whitespace-nowrap {
  white-space: nowrap;
}

/* 方案2: 使用 overflow 省略 */
.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 方案3: 控制换行行为 */
.break-words {
  word-break: break-word;      /* 英文长单词换行 */
  overflow-wrap: break-word;   /* 兼容写法 */
}

/* 方案4: 保持单词完整 */
.break-normal {
  word-break: normal;
  overflow-wrap: normal;
}
```

**Tailwind 类应用**:

```tsx
// 按钮文字不换行
<Button className="whitespace-nowrap">
  保存更改
</Button>

// 标签文字不换行，超长省略
<Tag className="max-w-[120px] truncate">
  超长标签名称
</Tag>

// 标题允许换行，但保持单词完整
<Title className="break-words">
  ThisIsAVeryLongWordThatNeedsToWrap
</Title>

// 表格单元格不换行
<TableCell className="whitespace-nowrap">
  2026-04-06
</TableCell>
```

**组件级规范**:

| 组件 | 换行策略 | Tailwind 类 |
|------|----------|-------------|
| Button | 不换行 | `whitespace-nowrap` |
| Tag/Badge | 不换行，超长省略 | `truncate` |
| 导航项 | 不换行 | `whitespace-nowrap` |
| 表单标签 | 不换行 | `whitespace-nowrap` |
| 数据值 | 按类型决定 | 日期 `nowrap`, 描述 `break-words` |
| 标题 H1-H3 | 允许换行 | `break-words` |
| 正文段落 | 允许换行 | `break-words` |

#### 2. 文字溢出处理

```tsx
// 单行省略
<p className="truncate">
  这是一段很长的文字，超出容器宽度应该显示省略号
</p>

// 多行省略 (2行)
<p className="line-clamp-2">
  这是一段很长的文字，
  超出2行应该显示省略号
</p>

// 弹性容器内的文字
<div className="flex min-w-0">
  <span className="truncate">
    文字内容
  </span>
</div>
```

#### 3. 文字对齐一致性

```
检查点:
□ 表单标签对齐方式一致（左对齐/右对齐）
□ 表格列头与内容对齐一致
□ 按钮文字居中对齐
□ 卡片内文字对齐统一
```

### 布局走查

#### 1. 间距一致性

```
检查点:
□ 使用设计系统预设间距 (space-1, space-2, space-4)
□ 相邻模块间距一致
□ 卡片内边距统一
□ 表单字段间距统一
```

**常见问题**:
```css
/* ❌ 硬编码间距 */
margin: 10px;
padding: 15px;

/* ✅ 使用设计系统 */
margin: theme('spacing.4');  /* 16px */
padding: theme('spacing.6'); /* 24px */
```

#### 2. 对齐检查

```
检查点:
□ 元素水平对齐（左/中/右）
□ 元素垂直对齐（顶/中/底）
□ 栅格对齐
□ 基线对齐（文字混排时）
```

#### 3. 响应式断点

```
检查点:
□ 375px - 移动端布局正常
□ 768px - 平板布局正常
□ 1024px - 桌面布局正常
□ 1440px - 大屏布局正常
□ 无横向滚动条
□ 触控目标 >= 44px
```

### 组件走查

#### Button 按钮

```
检查清单:
□ 高度符合规范 (sm: 32px, default: 40px, lg: 44px)
□ 内边距对称 (px-4)
□ 文字不换行
□ 图标与文字间距 (gap-2)
□ 加载状态有 spinner
□ 禁用状态样式正确
□ 悬停/点击反馈明显
```

#### Input 输入框

```
检查清单:
□ 高度统一 (40px)
□ 内边距一致 (px-3)
□ 聚焦状态边框明显
□ 错误状态提示清晰
□ Placeholder 颜色正确
□ 图标对齐居中
```

#### Card 卡片

```
检查清单:
□ 圆角统一 (rounded-lg)
□ 阴影符合规范
□ 内边距一致 (p-6)
□ 标题与内容间距
□ 底部操作区对齐
```

### 视觉走查

#### 1. 像素级对比

**方法**:
1. 打开 Figma Dev Mode
2. 在浏览器上使用 Pixel Perfect 插件
3. 叠加设计稿和实现效果
4. 检查差异

**检查项**:
```
□ 颜色值精确匹配
□ 间距精确匹配
□ 字体大小精确匹配
□ 圆角精确匹配
□ 阴影参数精确匹配
```

#### 2. 状态完整性

```
每个交互元素检查以下状态:
□ 默认状态 (Default)
□ 悬停状态 (Hover)
□ 聚焦状态 (Focus)
□ 激活/按下状态 (Active)
□ 禁用状态 (Disabled)
□ 加载状态 (Loading)
□ 错误状态 (Error)
```

### 数据场景走查

#### 1. 空状态

```tsx
// ✅ 良好的空状态
<EmptyState
  icon={<BookmarkIcon />}
  title="暂无书签"
  description="点击右上角按钮添加您的第一个书签"
  action={<Button>添加书签</Button>}
/>
```

#### 2. 超长数据

```tsx
// 测试数据场景
const testCases = {
  // 超长标题
  longTitle: "这是一个非常非常长的标题，测试标题显示和换行处理", 
  // 无空格长字符串
  longWord: "ThisIsAVeryLongWordThatMightCauseLayoutIssues",
  // 特殊字符
  specialChars: "<script>alert('xss')</script>",
  // emoji
  emoji: "🔥热门收藏💎精选内容🚀",
  // 混合内容
  mixed: "中文English日本語123!@#"
}
```

#### 3. 边界数据

```
测试场景:
□ 数量为 0
□ 数量为 1
□ 数量很大 (1000+)
□ 名称很短 (1个字符)
□ 名称很长 (100+字符)
□ 图片不存在/加载失败
□ 网络错误
```

### 走查报告模板

```markdown
## UI 走查报告

### 基本信息
- **页面/组件**: [名称]
- **检查日期**: YYYY-MM-DD
- **检查人**: @xxx
- **参考设计稿**: [Figma 链接]

### 浏览器环境
- **浏览器**: Chrome 120
- **分辨率**: 1440x900
- **系统**: macOS 14

### 问题列表

#### 🔴 严重问题 (必须修复)

**问题 1**: 按钮文字换行
- **位置**: 保存按钮
- **截图**: [截图]
- **问题描述**: 按钮文字"保存更改"在英文语言下换行显示为"Save\nChanges"
- **期望效果**: 文字不换行，保持在一行
- **修复建议**: 添加 `whitespace-nowrap` 类
- **优先级**: P0

#### 🟠 中等问题 (建议修复)

**问题 2**: 卡片间距不一致
- **位置**: 书签列表页
- **问题描述**: 卡片之间的间距有时是 16px，有时是 20px
- **期望效果**: 统一使用 16px (space-4)
- **修复建议**: 检查 Grid gap 设置

#### 🟡 轻微问题 (可延后)

**问题 3**: 加载状态缺少 spinner
- **位置**: 删除按钮
- **问题描述**: 删除操作时没有 loading 状态
- **修复建议**: 添加 loading spinner

### 数据统计
- 总问题数: 5
- 严重: 1
- 中等: 2
- 轻微: 2
- 已修复: 0

### 修复计划
| 问题 | 负责人 | 截止日期 | 状态 |
|------|--------|----------|------|
| 问题1 | @前端 | 今天 | 待修复 |
| 问题2 | @前端 | 本周 | 待修复 |

### 复查确认
- [ ] 所有严重问题已修复
- [ ] 视觉还原度达到 95%+
- [ ] 产品验收通过
```

### 走查工具推荐

| 工具 | 用途 | 链接 |
|------|------|------|
| Figma Dev Mode | 设计稿对比 | figma.com |
| PerfectPixel | 像素对比 | chrome 插件 |
| axe DevTools | 可访问性 | chrome 插件 |
| Page Ruler | 尺寸测量 | chrome 插件 |
| ColorPick Eyedropper | 颜色检查 | chrome 插件 |
| Responsive Viewer | 响应式测试 | chrome 插件 |

---

## 设计审查流程

### 审查清单

1. **视觉一致性**
   - [ ] 使用设计系统 Token
   - [ ] 间距一致
   - [ ] 圆角一致

2. **交互体验**
   - [ ] 悬停状态
   - [ ] 加载状态
   - [ ] 错误状态
   - [ ] 空状态

3. **响应式**
   - [ ] 移动端布局
   - [ ] 平板适配
   - [ ] 桌面端优化

4. **可访问性**
   - [ ] 键盘可访问
   - [ ] 颜色对比度
   - [ ] ARIA 标签

### 设计反馈模板

```markdown
## 设计审查反馈

### 问题 1: [组件/页面名称]
- **位置**: [具体位置]
- **问题**: [描述]
- **建议**: [改进方案]
- **优先级**: [高/中/低]

### 截图
[附截图]

### 参考
[相关设计参考]
```

---

## 设计-开发协作

### 交付清单

1. **设计稿**
   - [ ] Figma 链接
   - [ ] 标注尺寸和间距
   - [ ] 标注颜色 Token

2. **交互说明**
   - [ ] 状态变化（默认、悬停、禁用）
   - [ ] 动画时长和曲线
   - [ ] 响应式断点

3. **资源**
   - [ ] 图标（SVG）
   - [ ] 图片（优化后）
   - [ ] 字体文件（如需要）

### Token 映射

| Figma 变量 | CSS 变量 | Tailwind |
|------------|----------|----------|
| Primary/500 | --primary | bg-primary |
| Neutral/200 | --border | border-border |
| Text/Primary | --foreground | text-foreground |

---

## 最佳实践

### DO ✅

- 优先使用设计系统组件
- 保持组件职责单一
- 使用语义化 HTML
- 提供加载和错误状态
- 在真实数据下测试 UI

### DON'T ❌

- 硬编码颜色和尺寸
- 忽略空状态和错误状态
- 使用 display: none 隐藏交互元素
- 过度设计动画效果
- 忽视可访问性

---

## 常用工具

- **设计**: Figma
- **图标**: Lucide React
- **动画**: Motion (Framer Motion)
- **检查**: browser DevTools + axe DevTools
- **对比度**: WebAIM Contrast Checker

---

*版本: 1.0.0 | 适用项目: Bookmark Manager*

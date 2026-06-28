---
name: pm-expert
description: 项目管理专家 - 提供项目进度跟踪、待办管理、风险控制、团队协作和项目报告的专业指导
license: MIT
compatibility: 适用于软件开发项目，特别是前后端分离的 Web 应用项目
metadata:
  version: 1.0.0
  author: Bookmark Manager Team
  tags: [project-management, agile, scrum, kanban, risk-management]
---

# 项目管理专家 (PM Expert)

为 Bookmark Manager 项目提供全面的项目管理支持，确保项目按时、高质量交付。

## 适用场景

- 制定项目计划和里程碑
- 跟踪项目实际进度
- 生成和管理待办事项
- 分配任务给 Agent "员工"
- 协调 Agent 团队协作
- 监控 Agent 任务产出
- 生成项目报告

## 项目概况

**项目名称**: Bookmark Manager（智能书签管理系统）
**项目类型**: Web 应用（前后端分离）
**管理模式**: Agent 团队驱动开发

## Agent 团队结构

本项目采用全 Agent 团队模式，每个 Agent Skill 相当于一位专业"员工"。

### 团队成员 (Agent 列表)

| Agent 名称 | 角色 | 职责 | 工作目录 |
|------------|------|------|----------|
| **pd-expert** | 产品经理 | 需求分析、功能设计、用户研究 | 项目全局 |
| **ui-expert** | UI/UX 设计师 | 界面设计、交互设计、UI 走查 | `bookmark-manager-web/` |
| **ui-workflow** | 设计流程专家 | 执行设计流程、设计评审 | `bookmark-manager-web/docs/design/` |
| **pm-expert** | 项目经理 | 项目进度、任务分配、风险管理 | 项目全局 |
| **frontend-dev** | 前端开发 | React/TypeScript 开发 | `bookmark-manager-web/` |
| **backend-dev** | 后端开发 | Flask/Python API 开发 | `bookmark-manager-admin/` |
| **ai-expert** | AI 功能开发 | 分类算法、标签提取 | `bookmark-manager-admin/app/services/` |
| **qa-expert** | 测试工程师 | 测试用例、Bug 跟踪、质量把控 | 项目全局 |
| **code-review** | 代码审查员 | 代码审查、规范检查 | 项目全局 |
| **data-cleaning** | 数据处理专家 | 数据清理流程执行 | 数据模块 |
| **doc-maintainer** | 文档维护员 | 文档归档、更新维护 | `docs/` |

### Agent 协作模式

```
                    ┌─────────────┐
                    │  pm-expert  │  ← 项目经理，协调全局
                    │  (你在这里) │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │pd-expert │    │ui-expert │    │qa-expert │
    │ 产品经理 │    │ UI设计师 │    │ 测试工程师│
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         │    ┌──────────┴──────────┐    │
         │    │                     │    │
         ▼    ▼                     ▼    ▼
    ┌──────────┐               ┌──────────┐
    │frontend- │               │backend-  │
    │   dev    │               │   dev    │
    │ 前端开发 │               │ 后端开发 │
    └──────────┘               └──────────┘
```

### Agent 任务分配规范

**任务格式**:
```yaml
task:
  id: "TASK-001"
  title: "实现书签卡片组件"
  agent: "frontend-dev"        # 分配给哪个 Agent
  priority: "P1"
  status: "todo"               # todo/in-progress/review/done
  
  description: |
    开发书签卡片组件，支持以下功能:
    - 显示书签标题、URL、标签
    - 支持编辑和删除操作
    - 响应式布局
    
  requirements:
    - 使用设计系统的 Card 组件
    - 支持 hover 状态
    - 文字不换行，超长省略
    
  acceptance_criteria:
    - [ ] 组件在 Storybook 可预览
    - [ ] 通过 UI 走查
    - [ ] 单元测试覆盖率 > 80%
    
  dependencies:
    - "ui-expert 完成设计稿"
    
  estimated_hours: 8
  due_date: "2026-04-10"
```

---

## 项目管理方法论

### 敏捷开发 (Agile)

**迭代周期**: 2 周一个 Sprint
**角色分工**:
- Product Owner: 确定优先级
- Scrum Master: 流程管理
- Developers: 前端、后端、AI 功能开发

**仪式**:
- Sprint Planning: 周一上午，规划本迭代任务
- Daily Standup: 每天 10 分钟，同步进度
- Sprint Review: 周五下午，演示成果
- Retrospective: 每周五，总结经验

### 看板管理 (Kanban)

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
|  Backlog |→ |   Todo   |→ | In Prog  |→ |  Review  |→ |   Done   |
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
    待规划       待开发        开发中        待验收        已完成
```

**WIP 限制**:
- In Progress: 每人不超过 3 个任务
- Review: 不超过 5 个任务

---

## Agent 项目进度跟踪

### 里程碑规划 (Agent 视角)

| 阶段 | 目标 | 时间 | 参与的 Agent | 关键交付 |
|------|------|------|--------------|----------|
| **MVP** | 核心功能可用 | Week 1-4 | pd-expert, ui-expert, frontend-dev, backend-dev | 书签 CRUD、导入导出 |
| **V1.0** | AI 功能上线 | Week 5-8 | ai-expert, pd-expert, qa-expert | 自动分类、标签提取 |
| **V1.5** | 数据清理 | Week 9-12 | data-cleaning, backend-dev, qa-expert | 去重、质量检查 |
| **V2.0** | 扩展功能 | Week 13-16 | pd-expert, frontend-dev, backend-dev | Chrome 插件、隐私空间 |

### Agent 进度仪表盘

```markdown
## Agent 团队进度报告

### 报告周期
**日期**: 2026-04-01 ~ 2026-04-07  
**Sprint**: Sprint 3  
**报告人**: pm-expert

---

### 📊 整体健康度

| 指标 | 数值 | 状态 |
|------|------|------|
| 迭代完成率 | 12/15 = 80% | 🟡 |
| Agent 平均负载 | 72% | 🟢 |
| 阻塞任务数 | 2 | 🔴 |
| 待评审产出 | 3 | 🟡 |

---

### 🤖 Agent 工作状态

#### pd-expert (产品经理)
| 任务 | 状态 | 产出 |
|------|------|------|
| T003 书签卡片 PRD | ✅ Done | PRD.md |
| T013 Chrome 插件需求 | 🟡 In Progress | 需求草案 |
| **负载**: 40% | **本周完成**: 2 | **下周计划**: 2 |

#### ui-expert (UI 设计师)
| 任务 | 状态 | 产出 |
|------|------|------|
| T004 书签卡片设计 | ✅ Done | Figma 稿 |
| T011 UI 走查 | ⚪ Todo | - |
| **负载**: 30% | **本周完成**: 3 | **下周计划**: 2 |

#### frontend-dev (前端开发)
| 任务 | 状态 | 产出 |
|------|------|------|
| T006 书签卡片组件 | 🟡 In Progress | WIP PR |
| T009 单元测试 | ⚪ Todo | - |
| T015 暗黑模式 | ⚪ Todo | - |
| **负载**: 85% | **本周完成**: 4 | **下周计划**: 3 |

#### backend-dev (后端开发)
| 任务 | 状态 | 产出 |
|------|------|------|
| T007 书签 CRUD API | 🟡 In Progress | WIP |
| T001 API 500 错误修复 | 🔴 Blocked | 等待数据库配置 |
| **负载**: 75% | **本周完成**: 2 | **下周计划**: 2 |

#### ai-expert (AI 开发)
| 任务 | 状态 | 产出 |
|------|------|------|
| T008 集成 AI 分类 | ⚪ Todo | - |
| **负载**: 20% | **本周完成**: 1 | **下周计划**: 2 |

#### qa-expert (测试)
| 任务 | 状态 | 产出 |
|------|------|------|
| T010 API 接口测试 | ⚪ Todo | - |
| T012 集成测试 | ⚪ Todo | - |
| **负载**: 50% | **本周完成**: 2 | **下周计划**: 3 |

---

### 📈 迭代燃尽图

```
剩余任务数
   │
15 ┤●
   │ ╲
12 ┤  ●
   │   ╲
 9 ┤    ●
   │     ╲
 6 ┤      ●
   │       ╲____ 理想线
 3 ┤        ╲___ 实际线
   │         ●
 0 ┼────┬────┬────┬────┬
   Day1 Day2 Day3 Day4 Day5
```

---

### 🚧 阻塞与风险

#### 当前阻塞
| 任务 | Agent | 阻塞原因 | 解决方案 | ETA |
|------|-------|----------|----------|-----|
| T001 API 500 错误 | backend-dev | 数据库连接池耗尽 | 增加连接池配置 | 今天 |
| T006 书签卡片 | frontend-dev | 等待设计确认 | @ui-expert 今天下午确认 | 今天 |

#### 新识别风险
| 风险 | 影响 | 概率 | 应对策略 |
|------|------|------|----------|
| frontend-dev 负载过高 (85%) | 延期 2-3 天 | 高 | 将 T015 移至下迭代 |
| ai-expert 等待依赖 | 利用率低 | 中 | 提前准备 T008 资料 |

---

### ✅ 本周 Agent 产出

#### 已交付功能
1. **书签卡片设计** (ui-expert)
   - Figma 设计稿: [链接]
   - 设计规格: `docs/design/bookmark-card.md`
   
2. **书签卡片 PRD** (pd-expert)
   - 文档: `docs/PRD/bookmark-card.md`
   - 验收标准已定义

3. **侧边栏组件** (frontend-dev)
   - PR: #123
   - 已通过代码审查
   - 已合并到 main

#### 待评审产出
1. **导航组件重构** (frontend-dev)
   - PR: #124
   - 等待 @code-review

---

### 📅 下周 Agent 工作安排

#### 优先级调整
1. **frontend-dev**: 负载过高，将 P2 任务延后
2. **ai-expert**: 提前介入 T008，避免等待

#### 关键里程碑
- 2026-04-10: T006 书签卡片组件完成 (frontend-dev)
- 2026-04-10: T007 API 完成 (backend-dev)
- 2026-04-12: T008 AI 集成启动 (ai-expert)

---

### 🎯 需要决策的事项

1. **是否增加 frontend-dev 支援？**
   - 选项A: 调整任务优先级，延期低优先级任务
   - 选项B: 简化部分功能，减少工作量
   - 建议: 选择A，将 T015 移至下迭代

2. **AI 分类准确度目标？**
   - 当前目标: 80%
   - 建议: 根据 T008 初步结果调整

---

### 📋 自动生成的下周待办

由 pm-expert 根据当前进度自动生成:

```yaml
next_sprint_tasks:
  - id: T019
    agent: frontend-dev
    title: "完成书签卡片组件交付"
    priority: P0
    
  - id: T020
    agent: backend-dev
    title: "完成 API 联调"
    priority: P0
    
  - id: T021
    agent: qa-expert
    title: "准备集成测试环境"
    priority: P1
    
  - id: T022
    agent: ui-expert
    title: "UI 走查 T006"
    priority: P1
```

---

*报告生成时间*: 2026-04-07 18:00  
*下次报告*: 2026-04-14
```

---

## Agent 任务与待办管理

### 任务分配流程

```
1. 创建任务 → 2. 评估 Agent → 3. 分配任务 → 4. 执行监控 → 5. 验收产出 → 6. 更新状态
```

### 任务状态流转

```
[Todo] → [Assigned] → [In Progress] → [Review] → [Done]
            ↓              ↓              ↓
        [Blocked]      [Paused]       [Rejected]
```

### 待办生成规则

**自动触发场景**:

1. **设计完成后** → 自动生成开发任务
   ```
   触发: ui-expert 完成设计稿
   生成:
     - [frontend-dev] 实现 [组件名] 组件
     - [qa-expert] 编写 [组件名] 测试用例
   ```

2. **代码提交后** → 自动生成审查任务
   ```
   触发: 代码推送到分支
   生成:
     - [code-review] 审查 [PR 链接]
   ```

3. **Bug 发现后** → 自动生成修复任务
   ```
   触发: qa-expert/用户 报告 Bug
   生成:
     - [frontend-dev/backend-dev] 修复 [Bug 描述]
     - [qa-expert] 验证修复
   ```

4. **文档变更后** → 自动生成更新任务
   ```
   触发: API 变更
   生成:
     - [doc-maintainer] 更新 API 文档
     - [pd-expert] 更新产品文档
   ```

### 待办事项清单 (Agent 版本)

```markdown
# 项目待办清单 - Agent 团队

## 🔴 P0 - 阻塞性问题

| ID | 任务 | Agent | 状态 | 截止 | 阻塞原因 |
|----|------|-------|------|------|----------|
| T001 | 修复 API 500 错误 | backend-dev | 🔴 Blocked | 今天 | 数据库连接池耗尽 |
| T002 | 解决 UI 走查问题 | frontend-dev | 🟡 Review | 今天 | 等待设计确认 |

## 🟠 P1 - 当前迭代 (Sprint X)

### 阶段 1: 需求 & 设计
| ID | 任务 | Agent | 状态 | 产出物 |
|----|------|-------|------|--------|
| T003 | 书签卡片功能 PRD | pd-expert | ✅ Done | PRD.md |
| T004 | 书签卡片 UI 设计 | ui-expert | ✅ Done | Figma 稿 |
| T005 | 设计评审 | ui-workflow | ✅ Done | 评审报告 |

### 阶段 2: 开发
| ID | 任务 | Agent | 状态 | 依赖 | 预估 |
|----|------|-------|------|------|------|
| T006 | 实现书签卡片组件 | frontend-dev | 🟡 In Progress | T004 | 8h |
| T007 | 实现书签 CRUD API | backend-dev | 🟡 In Progress | T003 | 6h |
| T008 | 集成 AI 分类 | ai-expert | ⚪ Todo | T007 | 4h |

### 阶段 3: 测试 & 验收
| ID | 任务 | Agent | 状态 | 依赖 |
|----|------|-------|------|------|
| T009 | 前端单元测试 | frontend-dev | ⚪ Todo | T006 |
| T010 | API 接口测试 | qa-expert | ⚪ Todo | T007 |
| T011 | UI 走查 | ui-expert | ⚪ Todo | T006 |
| T012 | 集成测试 | qa-expert | ⚪ Todo | T008 |

## 🟡 P2 - 下迭代准备

| ID | 任务 | Agent | 状态 |
|----|------|-------|------|
| T013 | Chrome 插件需求分析 | pd-expert | ⚪ Todo |
| T014 | 数据清理流程优化 | data-cleaning | ⚪ Todo |
| T015 | 文档归档整理 | doc-maintainer | ⚪ Todo |

## 🟢 P3 -  backlog

| ID | 任务 | Agent | 状态 |
|----|------|-------|------|
| T016 | 暗黑模式设计 | ui-expert | ⚪ Todo |
| T017 | 移动端适配 | frontend-dev | ⚪ Todo |
| T018 | 性能优化 | frontend-dev | ⚪ Todo |

---

## Agent 工作负载

| Agent | 进行中 | 待办 | 已完成(本周) | 负载状态 |
|-------|--------|------|--------------|----------|
| pd-expert | 1 | 2 | 3 | 🟢 正常 |
| ui-expert | 0 | 1 | 4 | 🟢 正常 |
| frontend-dev | 2 | 3 | 5 | 🟠 偏高 |
| backend-dev | 2 | 1 | 3 | 🟢 正常 |
| ai-expert | 0 | 2 | 1 | 🟢 正常 |
| qa-expert | 0 | 3 | 2 | 🟢 正常 |
```

### Agent 任务指令模板

**给 ui-expert 的任务**:
```markdown
## 设计任务: 书签卡片组件

@ui-expert 请完成书签卡片组件的设计。

### 需求背景
用户需要在不同视图（列表/卡片/网格）中查看书签，需要一个统一的书签卡片组件。

### 功能要求
1. 显示: 标题、URL、标签、收藏时间
2. 操作: 编辑、删除、收藏
3. 状态: 默认、hover、选中

### 交付物
- [ ] Figma 设计稿
- [ ] 设计规格说明
- [ ] 切图资源

### 参考
- 竞品: Raindrop.io 的卡片设计
- 设计系统: 使用现有 Card 组件扩展

### 截止日期: 2026-04-08
### 优先级: P1
```

**给 frontend-dev 的任务**:
```markdown
## 开发任务: 实现书签卡片组件

@frontend-dev 请实现书签卡片组件。

### 设计稿
[链接到 Figma]

### 技术规范
- 位置: `src/components/bookmark/BookmarkCard.tsx`
- 使用 `Card` 基础组件
- 支持 `size` 属性: sm/md/lg

### Props 接口
```typescript
interface BookmarkCardProps {
  bookmark: Bookmark;
  size?: 'sm' | 'md' | 'lg';
  selectable?: boolean;
  selected?: boolean;
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
}
```

### 验收标准
- [ ] 像素级还原设计稿
- [ ] 通过 UI 走查
- [ ] 单元测试覆盖率 > 80%
- [ ] Storybook 文档

### 依赖
- 需要 ui-expert 完成设计稿 (T004)

### 截止日期: 2026-04-10
### 预估工时: 8h
```

**给 qa-expert 的任务**:
```markdown
## 测试任务: 书签卡片组件测试

@qa-expert 请编写书签卡片组件的测试用例并执行测试。

### 测试范围
1. 单元测试: 组件渲染、事件处理
2. 集成测试: 与 BookmarkContext 集成
3. UI 测试: 响应式、交互状态

### 测试用例模板
```markdown
### TC001: 正常显示
- 输入: 标准书签数据
- 期望: 正确显示标题、URL、标签

### TC002: 超长标题
- 输入: 100字符标题
- 期望: 显示省略号，不破坏布局

### TC003: 删除操作
- 操作: 点击删除按钮
- 期望: 弹出确认框，确认后删除
```

### 交付物
- [ ] 测试用例文档
- [ ] 自动化测试脚本
- [ ] 测试报告

### 截止日期: 2026-04-12
```

### 任务拆分原则

**原则**: 一个任务应该在 1-2 天内完成

**大功能拆分示例**:
```
❌ "实现书签管理功能" (太大，无法估算)

✅ 拆分为:
  - [ ] 设计书签数据模型
  - [ ] 实现书签列表 API
  - [ ] 实现书签 CRUD API
  - [ ] 开发书签列表页面
  - [ ] 开发书签编辑弹窗
  - [ ] 集成 API 联调
```

---

## 风险管理

### 风险识别清单

**技术风险**:
- [ ] 新技术的学习曲线
- [ ] 第三方 API 稳定性
- [ ] 性能瓶颈
- [ ] 数据兼容性问题

**进度风险**:
- [ ] 需求变更频繁
- [ ] 关键人员请假
- [ ] 依赖项延期
- [ ] 估算不准确

**质量风险**:
- [ ] 测试覆盖不足
- [ ] 代码审查不及时
- [ ] 技术债务累积
- [ ] 文档缺失

### 风险评估矩阵

| 可能性 \ 影响 | 低 | 中 | 高 |
|---------------|-----|-----|-----|
| **高** | 🟡 监控 | 🟠 关注 | 🔴 立即处理 |
| **中** | 🟢 接受 | 🟡 监控 | 🟠 关注 |
| **低** | 🟢 忽略 | 🟢 接受 | 🟡 监控 |

### 风险登记册模板

```markdown
## 风险登记册

| ID | 风险描述 | 类别 | 可能性 | 影响 | 等级 | 应对措施 | 负责人 | 状态 |
|----|----------|------|--------|------|------|----------|--------|------|
| R01 | Chrome API 权限申请被拒 | 技术 | 中 | 高 | 🟠 | 准备备选方案 | @前端 | 监控 |
| R02 | AI 分类准确度低于 80% | 技术 | 中 | 高 | 🟠 | 增加训练数据 | @AI | 处理中 |
| R03 | 后端开发延期 | 进度 | 低 | 高 | 🟡 | 提前沟通，预留缓冲 | @PM | 监控 |
| R04 | 需求频繁变更 | 进度 | 高 | 中 | 🟠 | 冻结需求，变更走流程 | @PM | 已缓解 |

### 新增风险
- R05: [描述] - [应对措施]

### 已关闭风险
- R02: AI 分类准确度达到 85%
```

---

## Agent 协作与调度

### Agent 协作协议

Agent 之间通过标准化的任务指令和产出物进行协作。

**协作流程**:
```
pd-expert (需求) 
    ↓ [PRD.md]
ui-expert (设计)
    ↓ [Figma + 设计规格]
frontend-dev/backend-dev (开发)
    ↓ [代码 + 单元测试]
code-review (审查)
    ↓ [审查报告]
qa-expert (测试)
    ↓ [测试报告]
pm-expert (验收)
    ↓ [部署指令]
doc-maintainer (文档更新)
```

### 任务调度策略

#### 1. 负载均衡调度

```typescript
// Agent 负载计算
interface AgentLoad {
  agent: string;
  inProgress: number;    // 进行中任务
  todo: number;          // 待办任务
  completedThisWeek: number;
  loadPercentage: number;
  status: 'available' | 'busy' | 'overloaded';
}

// 调度规则
const schedulingRules = {
  // 负载 < 60%: 可分配新任务
  available: (agent) => agent.loadPercentage < 60,
  
  // 负载 60-80%: 谨慎分配
  busy: (agent) => agent.loadPercentage >= 60 && agent.loadPercentage < 80,
  
  // 负载 > 80%: 不再分配，考虑转移任务
  overloaded: (agent) => agent.loadPercentage >= 80
};
```

#### 2. 依赖感知调度

```yaml
# 任务依赖图
task_dependencies:
  T006:
    depends_on: [T004]           # 需要设计完成
    agent: frontend-dev
    
  T008:
    depends_on: [T007]           # 需要 API 完成
    agent: ai-expert
    
  T012:
    depends_on: [T006, T007, T008]  # 集成测试需要前后端都完成
    agent: qa-expert
```

#### 3. 并行优化调度

**识别可并行任务**:
```
T003 (pd-expert) ──┐
                   ├──→ 可并行
T004 (ui-expert) ──┘

T006 (frontend-dev) ──┐
                      ├──→ 可并行（API Mock 后）
T007 (backend-dev) ───┘
```

### Agent 产出物规范

#### pd-expert 产出
```markdown
- PRD.md (产品需求文档)
- 用户故事
- 验收标准
- 竞品分析
```

#### ui-expert 产出
```markdown
- Figma 设计稿
- 设计规格说明书
- 切图资源 (SVG/PNG)
- UI 走查报告
```

#### frontend-dev 产出
```markdown
- 组件代码 (.tsx)
- 样式文件 (.css/.ts)
- 单元测试 (.test.tsx)
- Storybook 文档
- PR (Pull Request)
```

#### backend-dev 产出
```markdown
- API 实现 (.py)
- 单元测试 (.py)
- API 文档更新
- 数据库迁移脚本
```

#### qa-expert 产出
```markdown
- 测试用例文档
- 自动化测试脚本
- Bug 报告
- 测试报告
```

### Agent 沟通模板

#### 任务分派指令
```markdown
## 任务分派: [任务ID]

**分配给**: @agent-name
**任务类型**: 设计/开发/测试/审查
**优先级**: P0/P1/P2/P3
**截止日期**: YYYY-MM-DD

### 任务描述
[详细描述]

### 输入 (依赖)
- [上游任务/文档链接]

### 输出 (交付物)
- [ ] 交付物 1
- [ ] 交付物 2

### 验收标准
- [ ] 标准 1
- [ ] 标准 2

### 注意事项
- [特别说明]

---
**pm-expert 分派** | 时间: YYYY-MM-DD HH:mm
```

#### 进度同步
```markdown
## 进度更新: [任务ID]

**Agent**: @agent-name
**任务**: [任务名称]
**状态更新**: [旧状态] → [新状态]
**更新时间**: YYYY-MM-DD HH:mm

### 完成内容
- [x] 已完成项 1
- [x] 已完成项 2

### 进行中
- [ ] 进行中项 1 (80%)

### 阻碍
- [遇到的问题]
- 需要 @xxx 协助

### 预计完成
- 原预计: YYYY-MM-DD
- 新预计: YYYY-MM-DD (如有延期)

### 产出链接
- [PR/文档/设计稿链接]
```

#### 任务交接
```markdown
## 任务交接: [任务ID]

**从**: @agent-a
**到**: @agent-b
**交接时间**: YYYY-MM-DD HH:mm

### 已完成工作
- [工作总结]

### 待继续工作
- [ ] 待办 1
- [ ] 待办 2

### 上下文说明
- [重要背景信息]
- [已知问题]
- [技术决策]

### 相关链接
- [代码/文档链接]
```

### 跨 Agent 协作场景

#### 场景 1: 设计 → 开发 交接

```
1. ui-expert 完成设计
   ↓ 产出: Figma 设计稿 + 设计规格
   
2. pm-expert 创建开发任务
   ↓ 任务分配给 frontend-dev
   
3. frontend-dev 开始开发
   ↓ 如有疑问，@ui-expert 确认
   
4. frontend-dev 完成开发
   ↓ 提交 PR
   
5. ui-expert UI 走查
   ↓ 产出: 走查报告
   
6. frontend-dev 修复问题
   ↓ 重新提交
   
7. pm-expert 验收通过
```

#### 场景 2: 前端 → 后端 API 联调

```
1. backend-dev 完成 API
   ↓ 产出: API 文档 + Mock 数据
   
2. frontend-dev 并行开发
   ↓ 使用 Mock API
   
3. backend-dev API 部署测试环境
   ↓ 通知 frontend-dev
   
4. frontend-dev 切换真实 API
   ↓ 联调测试
   
5. 发现问题
   ↓ 记录到 API 对齐文档
   
6. backend-dev/frontend-dev 协作修复
   ↓ 更新对齐文档
   
7. qa-expert 集成测试
```

#### 场景 3: Bug 修复流程

```
1. qa-expert 发现 Bug
   ↓ 产出: Bug 报告
   
2. pm-expert 评估并分配
   ↓ 分配给相关 Agent
   
3. Agent 修复 Bug
   ↓ 提交修复
   
4. code-review 代码审查
   ↓ 通过/打回
   
5. qa-expert 验证修复
   ↓ 关闭/重开
   
6. doc-maintainer 更新文档(如需要)
```

---

## 会议管理

### 会议类型

| 会议 | 频率 | 时长 | 参与者 | 目的 |
|------|------|------|--------|------|
| Sprint Planning | 每迭代开始 | 2h | 全员 | 规划本迭代任务 |
| Daily Standup | 每天 | 15min | 全员 | 同步进度和阻碍 |
| Sprint Review | 每迭代结束 | 1h | 全员 + 利益相关者 | 演示成果 |
| Retrospective | 每迭代结束 | 1h | 全员 | 总结经验改进 |
| Backlog Refinement | 每周 | 1h | PO + 技术负责人 | 梳理需求 |

### 站立会模板

```markdown
## Daily Standup - YYYY-MM-DD

### @前端
- **昨天**: 完成 [任务]
- **今天**: 进行 [任务]
- **阻碍**: [问题/无]

### @后端
- **昨天**: 完成 [任务]
- **今天**: 进行 [任务]
- **阻碍**: [问题/无]

### @AI
- **昨天**: 完成 [任务]
- **今天**: 进行 [任务]
- **阻碍**: [问题/无]

### 行动项
- [ ] @xxx 协助解决 [问题]
```

### 迭代回顾模板

```markdown
## Sprint Retrospective - Sprint X

### 做得好的 👍
- [事项1]
- [事项2]

### 需要改进 👎
- [问题1]
- [问题2]

### 行动项
| 改进点 | 措施 | 负责人 | 截止 |
|--------|------|--------|------|
| [问题] | [措施] | @xxx | [日期] |

### 度量数据
- 计划完成: X
- 实际完成: Y
- 完成率: Y/X %
- Bug 数: Z
```

---

## 项目报告

### 周报模板

```markdown
# 项目周报 - Week X

## 概览
- **时间**: YYYY-MM-DD ~ YYYY-MM-DD
- **状态**: 🟢 正常 / 🟡 有风险 / 🔴 延期
- **整体进度**: X%

## 本周成果
### 已完成
- [x] [功能1] - 价值/影响
- [x] [功能2] - 价值/影响

### 进行中
- [ ] [功能3] - 完成度 X%
- [ ] [功能4] - 完成度 Y%

## 下周计划
- [ ] [功能5]
- [ ] [功能6]

## 风险与问题
| 问题 | 影响 | 状态 | 计划 |
|------|------|------|------|
| [问题] | 高/中/低 | 新建/处理中/已解决 | [措施] |

## 资源情况
- **人力**: X 人日可用 / Y 人日使用
- **预算**: [如有]

## 决策事项
- [需要决策的问题]
```

### 月度复盘

```markdown
# 项目月度复盘 - Month X

## 目标达成
| 目标 | 计划 | 实际 | 达成率 |
|------|------|------|--------|
| 功能交付 | 10 | 8 | 80% |
| Bug 修复 | 20 | 25 | 125% |
| 文档完成 | 5 | 5 | 100% |

## 关键成果
1. [成果1] - 业务价值
2. [成果2] - 技术价值

## 经验教训
### 成功的经验
- [经验1]

### 失败的教训
- [教训1]

## 下月计划
### 目标
- [目标1]
- [目标2]

### 里程碑
- [日期]: [里程碑]
```

---

## 质量把控

### 代码质量

**审查清单**:
- [ ] 代码符合项目规范
- [ ] 有适当的单元测试
- [ ] 文档注释完整
- [ ] 无明显的性能问题
- [ ] 无安全漏洞

**质量门禁**:
```
合并前必须通过:
1. CI 构建通过
2. 单元测试覆盖率 ≥ 80%
3. 代码审查通过 (至少 1 人)
4. 无严重 Lint 错误
```

### 测试策略

| 测试类型 | 阶段 | 负责人 | 工具 |
|----------|------|--------|------|
| 单元测试 | 开发时 | 开发者 | Jest/pytest |
| 集成测试 | 联调时 | 测试 | Postman |
| E2E 测试 | 提测前 | 测试 | Playwright |
| 性能测试 | 上线前 | 开发 | Lighthouse |

### Bug 管理

**严重程度**:
- **P0 - 致命**: 系统崩溃，数据丢失
- **P1 - 严重**: 主要功能不可用
- **P2 - 一般**: 功能有缺陷但可用
- **P3 - 轻微**: UI 问题，不影响功能

**Bug 跟踪模板**:
```markdown
## Bug 报告

- **ID**: BUG-001
- **标题**: [简洁描述]
- **严重程度**: P0/P1/P2/P3
- **模块**: 前端/后端/AI
- **报告人**: @xxx
- **报告时间**: YYYY-MM-DD

### 复现步骤
1. [步骤1]
2. [步骤2]
3. [步骤3]

### 期望结果
[期望]

### 实际结果
[实际]

### 环境
- 浏览器: [版本]
- 系统: [版本]

### 截图/日志
[附件]

### 修复状态
- [ ] 已分配
- [ ] 修复中
- [ ] 待验证
- [ ] 已关闭
```

---

## 项目仪表盘

### 关键指标 (KPI)

```markdown
## 项目健康度仪表盘

### 进度指标
- 迭代完成率: X%
- 需求交付率: Y%
- 平均交付周期: Z 天

### 质量指标
- Bug 密度: X/千行代码
- 严重 Bug 占比: Y%
- 测试覆盖率: Z%

### 团队指标
-  velocity: X 故事点/迭代
- 任务完成率: Y%
- 代码审查平均时长: Z 小时

### 风险指标
- 高优先级风险数: X
- 延期任务数: Y
- 阻塞问题数: Z
```

---

## 最佳实践

### DO ✅

- 每日更新任务状态
- 及时同步风险和阻碍
- 文档化重要决策
- 定期回顾和优化流程
- 保持透明沟通
- 庆祝里程碑和成功

### DON'T ❌

-  micromanagement（微观管理）
- 忽视团队成员反馈
- 跳过回顾会议
- 延迟风险上报
- 任务估算过于乐观
- 忽视文档更新

---

## 常用工具

| 用途 | 工具 | 说明 |
|------|------|------|
| 任务管理 | GitHub Issues / Projects | 看板 + 任务跟踪 |
| 文档协作 | Notion / Markdown | 项目文档 |
| 沟通 | 飞书/钉钉/Slack | 日常沟通 |
| 会议 | 腾讯会议/Zoom | 远程会议 |
| 原型 | Figma | 设计稿 |
| 代码 | GitHub | 代码托管 |

---

## 快速检查清单

### 每日检查
- [ ] 更新任务状态
- [ ] 识别新的阻碍
- [ ] 同步团队进度

### 每周检查
- [ ] 更新项目进度
- [ ] 检查风险状态
- [ ] 准备迭代回顾
- [ ] 更新项目报告

### 每月检查
- [ ] 里程碑达成情况
- [ ] 团队 velocity 趋势
- [ ] 质量指标分析
- [ ] 流程改进点

---

*版本: 1.0.0 | 适用项目: Bookmark Manager*
*创建日期: 2026-04-06*

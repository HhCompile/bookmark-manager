---
name: data-cleaning
description: 书签数据清理流程 - 去重、分类、质量检查
type: flow
---

# 数据清理流程

针对 Bookmark Manager 的书签数据清理工作流，包括去重、分类整理和质量检查。

## 适用场景

- 导入浏览器书签后的数据整理
- 定期数据维护
- 清理无效链接
- 重新分类书签

## 流程图（D2 格式 - 使用容器分组）

```d2
# 容器分组展示
DataImport: {
  label: |md
    **数据导入阶段**
  |
  style.fill: "#e3f2fd"
  style.stroke: "#1976d2"
  style.stroke-width: 2
  
  BEGIN: {
    shape: oval
    label: 开始清理
  }
  
  LOAD_DATA: {
    label: |md
      加载书签数据
      - 读取 bookmarks.json
      - 解析 HTML 导入文件
    |
  }
  
  BEGIN -> LOAD_DATA
}

PreProcessing: {
  label: |md
    **预处理阶段**
  |
  style.fill: "#fff3e0"
  style.stroke: "#f57c00"
  style.stroke-width: 2
  
  CHECK_DUPLICATE: {
    shape: diamond
    label: 发现重复URL?
  }
  
  DEDUP: {
    label: |md
      去重处理
      - 保留最新
      - 合并标签
    |
  }
  
  CHECK_DUPLICATE -> DEDUP: 是
}

Classification: {
  label: |md
    **智能分类阶段**
  |
  style.fill: "#e8f5e9"
  style.stroke: "#388e3c"
  style.stroke-width: 2
  
  AUTO_CLASS: {
    label: |md
      自动分类
      - AI 分析内容
      - 关键词匹配
      - 推荐分类
    |
  }
  
  MANUAL_REVIEW: {
    shape: diamond
    label: 需要人工确认?
  }
  
  CONFIRM_CAT: {
    label: 确认/修改分类
  }
  
  AUTO_CLASS -> MANUAL_REVIEW
  MANUAL_REVIEW -> CONFIRM_CAT: 是
}

QualityCheck: {
  label: |md
    **质量检查阶段**
  |
  style.fill: "#fce4ec"
  style.stroke: "#c2185b"
  style.stroke-width: 2
  
  CHECK_DEAD: {
    label: |md
      检测失效链接
      - HTTP 状态检查
      - 超时检测
    |
  }
  
  HAS_DEAD: {
    shape: diamond
    label: 发现失效链接?
  }
  
  MARK_DEAD: {
    label: 标记/删除死链
  }
  
  CHECK_QUALITY: {
    label: |md
      质量评分
      - 标题完整性
      - 描述质量
      - 标签丰富度
    |
  }
  
  CHECK_DEAD -> HAS_DEAD
  HAS_DEAD -> MARK_DEAD: 是
  MARK_DEAD -> CHECK_QUALITY
  HAS_DEAD -> CHECK_QUALITY: 无
}

Final: {
  label: |md
    **完成阶段**
  |
  style.fill: "#f3e5f5"
  style.stroke: "#7b1fa2"
  style.stroke-width: 2
  
  SAVE: {
    label: |md
      保存结果
      - 原子写入
      - 创建备份
    |
  }
  
  REPORT: {
    label: |md
      生成报告
      - 处理统计
      - 变更日志
    |
  }
  
  END: {
    shape: oval
    label: 清理完成
  }
  
  SAVE -> REPORT -> END
}

# 跨容器连接
DataImport.LOAD_DATA -> PreProcessing.CHECK_DUPLICATE
PreProcessing.CHECK_DUPLICATE -> Classification.AUTO_CLASS: 否
PreProcessing.DEDUP -> Classification.AUTO_CLASS
Classification.MANUAL_REVIEW -> QualityCheck.CHECK_DEAD: 否
Classification.CONFIRM_CAT -> QualityCheck.CHECK_DEAD
QualityCheck.CHECK_QUALITY -> Final.SAVE
```

## 各阶段说明

### 1. 数据导入

支持的数据源：
- `bookmarks.json` - 本地数据文件
- Chrome 书签导出 HTML
- 其他浏览器格式

### 2. 预处理

**去重规则**：
- 以 URL 为唯一标识
- 保留最后修改时间最新的
- 合并多个来源的标签

```python
# 去重示例逻辑
def deduplicate(bookmarks):
    seen = {}
    for bm in bookmarks:
        url = bm['url']
        if url in seen:
            # 合并标签，保留最新
            seen[url]['tags'] = list(set(seen[url]['tags'] + bm['tags']))
            if bm['updated_at'] > seen[url]['updated_at']:
                seen[url].update(bm)
        else:
            seen[url] = bm
    return list(seen.values())
```

### 3. 智能分类

**分类维度**：
- 技术/编程
- 设计/UI
- 工具/资源
- 学习/教程
- 娱乐/其他

**自动分类依据**：
- 网页内容分析
- URL 模式匹配
- 已有标签推断

### 4. 质量检查

**失效链接检测**：
- HTTP HEAD 请求
- 超时设置 5 秒
- 4xx/5xx 状态码标记

**质量评分标准**：
| 维度 | 权重 | 说明 |
|------|------|------|
| 标题完整 | 30% | 非空且有意义 |
| 描述质量 | 30% | 有描述且准确 |
| 标签数量 | 20% | 1-5 个标签 |
| 分类准确 | 20% | 分类符合内容 |

### 5. 保存与报告

**原子写入**：
```python
# 先写入临时文件，再重命名
import os
import shutil

def atomic_write(filepath, data):
    temp = filepath + '.tmp'
    with open(temp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    shutil.move(temp, filepath)
```

**备份机制**：
- 保留最近 5 个备份
- 命名格式：`bookmarks.json.bak.{n}`

## 输出报告示例

```markdown
# 数据清理报告

## 执行摘要
- 处理书签总数: 1,234
- 耗时: 45 秒

## 去重结果
- 发现重复: 23 组
- 合并标签: 45 个
- 去重后数量: 1,211

## 分类结果
- 自动分类: 856
- 待确认: 45
- 无分类: 310

## 质量检查
- 失效链接: 12
- 高质量 (>80分): 789
- 需改进: 422

## 建议
1. 手动确认 45 个待分类书签
2. 处理 12 个失效链接
3. 为 200+ 无描述书签添加描述
```

## 使用方式

```
/flow:data-cleaning
```

AI 将引导你逐步完成数据清理流程。

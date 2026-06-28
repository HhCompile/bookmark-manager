#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 分析器
分析 React/Tailwind 组件结构和样式
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ComponentInfo:
    """组件信息"""
    name: str
    file_path: str
    props: List[Dict[str, Any]]
    hooks: List[str]
    imports: List[str]
    tailwind_classes: List[str]
    complexity_score: int
    suggestions: List[str]


@dataclass
class DesignToken:
    """设计 Token"""
    category: str
    name: str
    value: str
    usage_count: int


class UIAnalyzer:
    """UI 组件分析器"""
    
    # Tailwind 类别映射
    TAILWIND_CATEGORIES = {
        'layout': ['flex', 'grid', 'block', 'inline', 'hidden', 'container', 'columns'],
        'spacing': ['p-', 'px-', 'py-', 'm-', 'mx-', 'my-', 'gap-', 'space-'],
        'sizing': ['w-', 'h-', 'min-', 'max-', 'size-'],
        'typography': ['text-', 'font-', 'leading-', 'tracking-', 'truncate'],
        'colors': ['bg-', 'text-', 'border-', 'from-', 'to-', 'via-'],
        'borders': ['rounded', 'border', 'outline', 'ring'],
        'effects': ['shadow', 'opacity', 'blur', 'grayscale'],
        'transforms': ['scale', 'rotate', 'translate', 'skew'],
        'transitions': ['transition', 'duration', 'ease', 'delay'],
        'responsive': ['sm:', 'md:', 'lg:', 'xl:', '2xl:'],
        'states': ['hover:', 'focus:', 'active:', 'disabled:', 'dark:'],
    }
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontend_root = self.project_root / "bookmark-manager-web"
        self.src_dir = self.frontend_root / "src"
    
    def analyze_component(self, file_path: str) -> Dict[str, Any]:
        """分析单个组件"""
        full_path = self._resolve_path(file_path)
        
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        content = full_path.read_text(encoding='utf-8')
        
        # 提取组件信息
        component_name = self._extract_component_name(content, full_path)
        props = self._extract_props(content)
        hooks = self._extract_hooks(content)
        imports = self._extract_imports(content)
        tailwind_classes = self._extract_tailwind_classes(content)
        complexity_score = self._calculate_complexity(content)
        suggestions = self._generate_suggestions(content, tailwind_classes)
        
        component_info = ComponentInfo(
            name=component_name,
            file_path=str(file_path),
            props=props,
            hooks=hooks,
            imports=imports,
            tailwind_classes=list(tailwind_classes),
            complexity_score=complexity_score,
            suggestions=suggestions
        )
        
        return asdict(component_info)
    
    def list_components(self, directory: str = "src/components") -> List[Dict]:
        """列出所有组件"""
        components_dir = self.frontend_root / directory
        components = []
        
        if not components_dir.exists():
            return []
        
        for file_path in components_dir.rglob("*.tsx"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.frontend_root)
                components.append({
                    "name": file_path.stem,
                    "path": str(relative_path),
                    "size": file_path.stat().st_size
                })
        
        return sorted(components, key=lambda x: x["name"])
    
    def extract_design_tokens(self) -> Dict[str, List[DesignToken]]:
        """提取设计 tokens"""
        tokens = {
            "colors": [],
            "spacing": [],
            "typography": [],
            "borders": [],
            "shadows": []
        }
        
        # 分析所有组件文件
        for file_path in self.src_dir.rglob("*.tsx"):
            if file_path.is_file():
                content = file_path.read_text(encoding='utf-8')
                self._extract_tokens_from_content(content, tokens)
        
        # 去重并统计使用频率
        for category in tokens:
            token_dict = {}
            for token in tokens[category]:
                key = f"{token.name}:{token.value}"
                if key in token_dict:
                    token_dict[key].usage_count += token.usage_count
                else:
                    token_dict[key] = token
            tokens[category] = sorted(
                token_dict.values(), 
                key=lambda x: x.usage_count, 
                reverse=True
            )[:20]  # 只保留前20个
        
        return {
            category: [asdict(t) for t in token_list]
            for category, token_list in tokens.items()
        }
    
    def suggest_improvements(self, file_path: str) -> List[Dict]:
        """提供改进建议"""
        full_path = self._resolve_path(file_path)
        content = full_path.read_text(encoding='utf-8')
        
        suggestions = []
        
        # 检查是否有硬编码的颜色
        if re.search(r'#[0-9A-Fa-f]{3,6}|rgb\(|hsl\(', content):
            suggestions.append({
                "type": "design_system",
                "severity": "warning",
                "message": "检测到硬编码颜色，建议使用设计系统的颜色变量",
                "suggestion": "使用 Tailwind 的颜色类（如 bg-blue-500）或 CSS 变量"
            })
        
        # 检查是否有内联样式
        if 'style={' in content:
            suggestions.append({
                "type": "best_practice",
                "severity": "info",
                "message": "检测到内联样式",
                "suggestion": "尽可能使用 Tailwind 类代替内联样式"
            })
        
        # 检查组件复杂度
        lines = content.split('\n')
        if len(lines) > 200:
            suggestions.append({
                "type": "refactoring",
                "severity": "warning",
                "message": f"组件代码较长（{len(lines)} 行），建议拆分",
                "suggestion": "将复杂组件拆分为更小的子组件"
            })
        
        # 检查是否有 aria 属性
        if 'aria-' not in content and 'role=' not in content:
            suggestions.append({
                "type": "accessibility",
                "severity": "warning",
                "message": "缺少无障碍属性",
                "suggestion": "添加 aria-label、role 等属性提升可访问性"
            })
        
        # 检查 Tailwind 类组织
        tailwind_pattern = r'className=["\']([^"\']+)["\']'
        matches = re.findall(tailwind_pattern, content)
        for class_string in matches:
            classes = class_string.split()
            if len(classes) > 15:
                suggestions.append({
                    "type": "maintainability",
                    "severity": "info",
                    "message": f"检测到较长的 className（{len(classes)} 个类）",
                    "suggestion": "使用 cn() 工具函数或提取为常量"
                })
                break
        
        return suggestions
    
    def _resolve_path(self, file_path: str) -> Path:
        """解析文件路径"""
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self.frontend_root / path
    
    def _extract_component_name(self, content: str, file_path: Path) -> str:
        """提取组件名称"""
        # 从文件内容中提取
        patterns = [
            r'export\s+default\s+function\s+(\w+)',
            r'export\s+const\s+(\w+)\s*=',
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\(',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        # 使用文件名
        return file_path.stem
    
    def _extract_props(self, content: str) -> List[Dict[str, Any]]:
        """提取 props 定义"""
        props = []
        
        # 匹配 interface 定义
        interface_pattern = r'interface\s+(\w+Props?)\s*\{([^}]+)\}'
        for match in re.finditer(interface_pattern, content, re.DOTALL):
            props_text = match.group(2)
            for line in props_text.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('//'):
                    parts = line.split(':', 1)
                    prop_name = parts[0].strip()
                    prop_type = parts[1].strip().rstrip(';?')
                    optional = '?' in line
                    props.append({
                        "name": prop_name,
                        "type": prop_type,
                        "optional": optional
                    })
        
        return props
    
    def _extract_hooks(self, content: str) -> List[str]:
        """提取使用的 hooks"""
        hooks = set()
        hook_pattern = r'use[A-Z][a-zA-Z]*'
        for match in re.finditer(hook_pattern, content):
            hooks.add(match.group())
        return sorted(list(hooks))
    
    def _extract_imports(self, content: str) -> List[str]:
        """提取 import 语句"""
        imports = []
        import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))
        return imports
    
    def _extract_tailwind_classes(self, content: str) -> set:
        """提取 Tailwind 类"""
        classes = set()
        
        # 匹配 className
        patterns = [
            r'className=["\']([^"\']+)["\']',
            r'className=\{[\`\']([^\`\']+)[\`\']\}',
            r'cn\(["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                class_string = match.group(1)
                # 处理模板字符串
                class_string = re.sub(r'\$\{[^}]+\}', '', class_string)
                classes.update(class_string.split())
        
        return classes
    
    def _calculate_complexity(self, content: str) -> int:
        """计算组件复杂度分数"""
        score = 0
        
        # 代码行数
        lines = len(content.split('\n'))
        score += lines // 50
        
        # 条件渲染
        score += len(re.findall(r'\?\s*<', content)) * 2
        
        # 状态管理
        score += len(re.findall(r'useState', content)) * 3
        
        # 副作用
        score += len(re.findall(r'useEffect', content)) * 2
        
        # 嵌套层级
        score += content.count('<') // 20
        
        return min(score, 100)  # 最高100分
    
    def _generate_suggestions(self, content: str, tailwind_classes: set) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 分析 Tailwind 使用
        categories = self._categorize_tailwind_classes(tailwind_classes)
        
        if len(categories.get('colors', [])) > 10:
            suggestions.append("颜色使用较多，建议统一设计系统")
        
        if 'responsive' not in categories or len(categories.get('responsive', [])) < 3:
            suggestions.append("建议添加更多响应式断点类")
        
        if 'states' not in categories:
            suggestions.append("建议添加交互状态样式（hover、focus）")
        
        return suggestions
    
    def _categorize_tailwind_classes(self, classes: set) -> Dict[str, List[str]]:
        """分类 Tailwind 类"""
        categories = {cat: [] for cat in self.TAILWIND_CATEGORIES.keys()}
        
        for cls in classes:
            for category, prefixes in self.TAILWIND_CATEGORIES.items():
                if any(cls.startswith(prefix) or prefix in cls for prefix in prefixes):
                    categories[category].append(cls)
                    break
        
        return categories
    
    def _extract_tokens_from_content(self, content: str, tokens: Dict):
        """从内容中提取设计 tokens"""
        # 提取颜色
        color_pattern = r'(bg|text|border|shadow)-([a-z]+-[0-9]+|current|transparent|white|black)'
        for match in re.finditer(color_pattern, content):
            token = DesignToken(
                category="colors",
                name=match.group(1),
                value=match.group(2),
                usage_count=1
            )
            tokens["colors"].append(token)
        
        # 提取间距
        spacing_pattern = r'(p|px|py|m|mx|my|gap)-([0-9]+|auto)'
        for match in re.finditer(spacing_pattern, content):
            token = DesignToken(
                category="spacing",
                name=match.group(1),
                value=match.group(2),
                usage_count=1
            )
            tokens["spacing"].append(token)
        
        # 提取字体大小
        font_pattern = r'text-([xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl]|[0-9]+)'
        for match in re.finditer(font_pattern, content):
            token = DesignToken(
                category="typography",
                name="text-size",
                value=match.group(1),
                usage_count=1
            )
            tokens["typography"].append(token)

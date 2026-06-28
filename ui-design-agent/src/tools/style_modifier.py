#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式修改器
修改现有组件的 Tailwind 样式
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class StyleModifier:
    """样式修改器"""
    
    # 预设样式方案
    STYLE_PRESETS = {
        "glass": {
            "description": "玻璃拟态风格",
            "replacements": {
                r'bg-(white|gray-\d+)': 'bg-white/70 backdrop-blur-md',
                r'border-gray-\d+': 'border-white/20',
                r'shadow-sm': 'shadow-lg',
            }
        },
        "neumorphism": {
            "description": "新拟态风格",
            "replacements": {
                r'bg-(white|gray-\d+)': 'bg-gray-100',
                r'shadow-sm': 'shadow-[4px_4px_10px_#bebebe,-4px_-4px_10px_#ffffff]',
                r'border': '',
            }
        },
        "minimal": {
            "description": "极简风格",
            "replacements": {
                r'bg-[a-z]+-\d+': 'bg-transparent',
                r'border-[a-z]+-\d+': 'border-gray-200',
                r'shadow-[a-z]+': '',
                r'rounded-[a-z]+': 'rounded-none',
            }
        },
        "rounded": {
            "description": "圆角风格",
            "replacements": {
                r'rounded-(none|sm)': 'rounded-2xl',
                r'rounded-md': 'rounded-xl',
            }
        },
        "dark": {
            "description": "深色主题",
            "replacements": {
                r'bg-white': 'bg-gray-900',
                r'bg-gray-\d+': 'bg-gray-800',
                r'text-gray-900': 'text-white',
                r'text-gray-700': 'text-gray-300',
                r'text-gray-600': 'text-gray-400',
                r'border-gray-\d+': 'border-gray-700',
            }
        },
        "colorful": {
            "description": "彩色渐变风格",
            "replacements": {
                r'bg-blue-\d+': 'bg-gradient-to-r from-blue-500 to-purple-600',
                r'bg-green-\d+': 'bg-gradient-to-r from-green-400 to-emerald-600',
                r'bg-red-\d+': 'bg-gradient-to-r from-red-500 to-pink-600',
            }
        },
        "compact": {
            "description": "紧凑风格",
            "replacements": {
                r'p-4': 'p-2',
                r'p-6': 'p-3',
                r'm-4': 'm-2',
                r'gap-4': 'gap-2',
                r'text-lg': 'text-sm',
            }
        },
        "spacious": {
            "description": "宽松风格",
            "replacements": {
                r'p-2': 'p-4',
                r'p-4': 'p-6',
                r'm-2': 'm-4',
                r'gap-2': 'gap-4',
                r'text-sm': 'text-base',
            }
        },
    }
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontend_root = self.project_root / "bookmark-manager-web"
    
    def modify_style(
        self, 
        file_path: str, 
        style_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """修改组件样式"""
        full_path = self._resolve_path(file_path)
        
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        content = full_path.read_text(encoding='utf-8')
        original_content = content
        
        # 应用样式变更
        changes_applied = []
        
        # 1. 应用预设方案
        if "preset" in style_changes:
            preset_name = style_changes["preset"]
            if preset_name in self.STYLE_PRESETS:
                preset = self.STYLE_PRESETS[preset_name]
                content, changes = self._apply_preset(content, preset)
                changes_applied.extend(changes)
        
        # 2. 应用自定义替换
        if "replacements" in style_changes:
            for pattern, replacement in style_changes["replacements"].items():
                new_content, count = self._replace_pattern(content, pattern, replacement)
                if count > 0:
                    content = new_content
                    changes_applied.append({
                        "pattern": pattern,
                        "replacement": replacement,
                        "count": count
                    })
        
        # 3. 应用特定的 className 修改
        if "className_changes" in style_changes:
            content, changes = self._apply_classname_changes(
                content, style_changes["className_changes"]
            )
            changes_applied.extend(changes)
        
        # 4. 添加新的类
        if "add_classes" in style_changes:
            content, changes = self._add_classes(content, style_changes["add_classes"])
            changes_applied.extend(changes)
        
        # 5. 移除类
        if "remove_classes" in style_changes:
            content, changes = self._remove_classes(content, style_changes["remove_classes"])
            changes_applied.extend(changes)
        
        # 保存修改
        if content != original_content:
            # 备份原文件
            backup_path = full_path.with_suffix('.tsx.backup')
            backup_path.write_text(original_content, encoding='utf-8')
            
            # 写入新内容
            full_path.write_text(content, encoding='utf-8')
        
        return {
            "file_path": str(full_path.relative_to(self.frontend_root)),
            "changes_applied": changes_applied,
            "total_changes": len(changes_applied),
            "modified": content != original_content
        }
    
    def apply_preset_style(self, file_path: str, preset_name: str) -> Dict[str, Any]:
        """应用预设样式"""
        if preset_name not in self.STYLE_PRESETS:
            return {
                "error": f"Unknown preset: {preset_name}",
                "available_presets": list(self.STYLE_PRESETS.keys())
            }
        
        return self.modify_style(file_path, {"preset": preset_name})
    
    def batch_modify(
        self, 
        directory: str, 
        style_changes: Dict[str, Any],
        file_pattern: str = "*.tsx"
    ) -> Dict[str, Any]:
        """批量修改目录中的组件样式"""
        dir_path = self.frontend_root / directory
        
        if not dir_path.exists():
            return {"error": f"Directory not found: {directory}"}
        
        results = []
        for file_path in dir_path.rglob(file_pattern):
            if file_path.is_file():
                result = self.modify_style(
                    str(file_path.relative_to(self.frontend_root)),
                    style_changes
                )
                results.append(result)
        
        return {
            "total_files": len(results),
            "modified_files": sum(1 for r in results if r.get("modified", False)),
            "results": results
        }
    
    def list_presets(self) -> List[Dict[str, str]]:
        """列出所有可用的样式预设"""
        return [
            {"name": name, "description": preset["description"]}
            for name, preset in self.STYLE_PRESETS.items()
        ]
    
    def preview_changes(
        self, 
        file_path: str, 
        style_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """预览样式变更（不保存）"""
        full_path = self._resolve_path(file_path)
        
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        content = full_path.read_text(encoding='utf-8')
        
        # 应用样式变更（不保存）
        if "preset" in style_changes:
            preset_name = style_changes["preset"]
            if preset_name in self.STYLE_PRESETS:
                preset = self.STYLE_PRESETS[preset_name]
                content, _ = self._apply_preset(content, preset)
        
        # 提取变更的 className 示例
        classnames_before = self._extract_classnames(original_content)
        classnames_after = self._extract_classnames(content)
        
        return {
            "file_path": str(full_path.relative_to(self.frontend_root)),
            "preview": content,
            "classnames_diff": {
                "before": list(classnames_before)[:20],
                "after": list(classnames_after)[:20]
            }
        }
    
    def _resolve_path(self, file_path: str) -> Path:
        """解析文件路径"""
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self.frontend_root / path
    
    def _apply_preset(self, content: str, preset: Dict) -> tuple:
        """应用预设样式"""
        changes = []
        
        for pattern, replacement in preset["replacements"].items():
            new_content, count = self._replace_pattern(content, pattern, replacement)
            if count > 0:
                content = new_content
                changes.append({
                    "pattern": pattern,
                    "replacement": replacement,
                    "count": count
                })
        
        return content, changes
    
    def _replace_pattern(self, content: str, pattern: str, replacement: str) -> tuple:
        """替换模式"""
        regex = re.compile(pattern)
        new_content, count = regex.subn(replacement, content)
        return new_content, count
    
    def _apply_classname_changes(
        self, 
        content: str, 
        classname_changes: Dict[str, str]
    ) -> tuple:
        """应用 className 修改"""
        changes = []
        
        # 匹配 className 属性
        classname_pattern = r'className=["\']([^"\']+)["\']'
        
        def replace_classname(match):
            original = match.group(1)
            modified = original
            
            for old_class, new_class in classname_changes.items():
                if old_class in modified:
                    modified = modified.replace(old_class, new_class)
                    changes.append({
                        "from": old_class,
                        "to": new_class
                    })
            
            return f'className="{modified}"'
        
        new_content = re.sub(classname_pattern, replace_classname, content)
        
        return new_content, changes
    
    def _add_classes(self, content: str, classes_to_add: Dict[str, List[str]]) -> tuple:
        """添加新类到特定元素"""
        changes = []
        
        # 按选择器添加类
        for selector, classes in classes_to_add.items():
            # 简单的实现：在包含 selector 的 className 后添加
            pattern = f'({re.escape(selector)}[^"\']*)["\']'
            
            def add_class(match):
                existing = match.group(1)
                new_classes = ' '.join(classes)
                return f'{existing} {new_classes}"'
            
            content = re.sub(pattern, add_class, content)
            changes.append({
                "selector": selector,
                "added": classes
            })
        
        return content, changes
    
    def _remove_classes(self, content: str, classes_to_remove: List[str]) -> tuple:
        """移除类"""
        changes = []
        
        for class_name in classes_to_remove:
            pattern = rf'\s*{re.escape(class_name)}\s*'
            new_content, count = re.subn(pattern, ' ', content)
            if count > 0:
                content = new_content
                changes.append({
                    "removed": class_name,
                    "count": count
                })
        
        # 清理多余空格
        content = re.sub(r'\s+', ' ', content)
        
        return content, changes
    
    def _extract_classnames(self, content: str) -> set:
        """提取所有 className"""
        classes = set()
        pattern = r'className=["\']([^"\']+)["\']'
        for match in re.finditer(pattern, content):
            classes.update(match.group(1).split())
        return classes

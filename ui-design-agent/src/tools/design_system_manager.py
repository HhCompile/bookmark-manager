#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设计系统管理器
管理设计 tokens、组件变体和主题
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DesignToken:
    """设计 Token"""
    name: str
    value: str
    category: str
    description: str = ""


class DesignSystemManager:
    """设计系统管理器"""
    
    # 默认设计 tokens
    DEFAULT_TOKENS = {
        "colors": {
            "primary": {
                "50": "#eff6ff",
                "100": "#dbeafe",
                "200": "#bfdbfe",
                "300": "#93c5fd",
                "400": "#60a5fa",
                "500": "#3b82f6",
                "600": "#2563eb",
                "700": "#1d4ed8",
                "800": "#1e40af",
                "900": "#1e3a8a",
            },
            "gray": {
                "50": "#f9fafb",
                "100": "#f3f4f6",
                "200": "#e5e7eb",
                "300": "#d1d5db",
                "400": "#9ca3af",
                "500": "#6b7280",
                "600": "#4b5563",
                "700": "#374151",
                "800": "#1f2937",
                "900": "#111827",
            }
        },
        "spacing": {
            "xs": "0.25rem",    # 4px
            "sm": "0.5rem",     # 8px
            "md": "1rem",       # 16px
            "lg": "1.5rem",     # 24px
            "xl": "2rem",       # 32px
            "2xl": "2.5rem",    # 40px
            "3xl": "3rem",      # 48px
        },
        "typography": {
            "fontFamily": {
                "sans": ["Inter", "system-ui", "sans-serif"],
                "mono": ["Fira Code", "Monaco", "monospace"],
            },
            "fontSize": {
                "xs": "0.75rem",
                "sm": "0.875rem",
                "base": "1rem",
                "lg": "1.125rem",
                "xl": "1.25rem",
                "2xl": "1.5rem",
                "3xl": "1.875rem",
            },
            "fontWeight": {
                "normal": "400",
                "medium": "500",
                "semibold": "600",
                "bold": "700",
            },
            "lineHeight": {
                "tight": "1.25",
                "normal": "1.5",
                "relaxed": "1.75",
            },
        },
        "borders": {
            "radius": {
                "none": "0",
                "sm": "0.25rem",
                "md": "0.375rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "2xl": "1rem",
                "full": "9999px",
            },
            "width": {
                "none": "0",
                "thin": "1px",
                "medium": "2px",
                "thick": "4px",
            },
        },
        "shadows": {
            "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            "md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
            "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
            "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
        },
        "transitions": {
            "duration": {
                "fast": "150ms",
                "normal": "300ms",
                "slow": "500ms",
            },
            "easing": {
                "default": "cubic-bezier(0.4, 0, 0.2, 1)",
                "in": "cubic-bezier(0.4, 0, 1, 1)",
                "out": "cubic-bezier(0, 0, 0.2, 1)",
            },
        },
    }
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "ui-design-agent" / "config"
        self.tokens_file = self.config_dir / "design_tokens.json"
        self.variants_file = self.config_dir / "component_variants.json"
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载或初始化 tokens
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict:
        """加载设计 tokens"""
        if self.tokens_file.exists():
            with open(self.tokens_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 使用默认 tokens
        return self.DEFAULT_TOKENS.copy()
    
    def _save_tokens(self):
        """保存设计 tokens"""
        with open(self.tokens_file, 'w', encoding='utf-8') as f:
            json.dump(self.tokens, f, indent=2, ensure_ascii=False)
    
    def get_tokens(self, category: Optional[str] = None) -> Dict:
        """获取设计 tokens"""
        if category:
            return self.tokens.get(category, {})
        return self.tokens
    
    def update_token(
        self, 
        category: str, 
        token_name: str, 
        token_value: Any
    ) -> Dict[str, Any]:
        """更新设计 token"""
        if category not in self.tokens:
            self.tokens[category] = {}
        
        # 处理嵌套 token（如 colors.primary.500）
        keys = token_name.split('.')
        current = self.tokens[category]
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        old_value = current.get(keys[-1])
        current[keys[-1]] = token_value
        
        # 保存
        self._save_tokens()
        
        return {
            "category": category,
            "token": token_name,
            "old_value": old_value,
            "new_value": token_value,
            "updated_at": datetime.now().isoformat()
        }
    
    def add_token_category(self, category: str, default_value: Dict = None) -> Dict:
        """添加新的 token 类别"""
        if category in self.tokens:
            return {"error": f"Category '{category}' already exists"}
        
        self.tokens[category] = default_value or {}
        self._save_tokens()
        
        return {
            "category": category,
            "message": f"Category '{category}' created successfully"
        }
    
    def delete_token(self, category: str, token_name: str) -> Dict:
        """删除设计 token"""
        if category not in self.tokens:
            return {"error": f"Category '{category}' not found"}
        
        keys = token_name.split('.')
        current = self.tokens[category]
        
        for key in keys[:-1]:
            if key not in current:
                return {"error": f"Token '{token_name}' not found"}
            current = current[key]
        
        if keys[-1] in current:
            deleted_value = current.pop(keys[-1])
            self._save_tokens()
            
            return {
                "category": category,
                "token": token_name,
                "deleted_value": deleted_value
            }
        
        return {"error": f"Token '{token_name}' not found"}
    
    def export_to_tailwind_config(self) -> Dict:
        """导出为 Tailwind CSS 配置"""
        config = {
            "theme": {
                "extend": {}
            }
        }
        
        # 转换颜色
        if "colors" in self.tokens:
            config["theme"]["extend"]["colors"] = self.tokens["colors"]
        
        # 转换间距
        if "spacing" in self.tokens:
            config["theme"]["extend"]["spacing"] = self.tokens["spacing"]
        
        # 转换字体
        if "typography" in self.tokens:
            typography = self.tokens["typography"]
            if "fontFamily" in typography:
                config["theme"]["extend"]["fontFamily"] = typography["fontFamily"]
            if "fontSize" in typography:
                config["theme"]["extend"]["fontSize"] = typography["fontSize"]
        
        # 转换圆角
        if "borders" in self.tokens and "radius" in self.tokens["borders"]:
            config["theme"]["extend"]["borderRadius"] = self.tokens["borders"]["radius"]
        
        # 转换阴影
        if "shadows" in self.tokens:
            config["theme"]["extend"]["boxShadow"] = self.tokens["shadows"]
        
        return config
    
    def generate_css_variables(self) -> str:
        """生成 CSS 变量"""
        css_lines = [":root {"]
        
        # 颜色变量
        if "colors" in self.tokens:
            for color_name, shades in self.tokens["colors"].items():
                if isinstance(shades, dict):
                    for shade, value in shades.items():
                        css_lines.append(f"  --color-{color_name}-{shade}: {value};")
                else:
                    css_lines.append(f"  --color-{color_name}: {shades};")
        
        # 间距变量
        if "spacing" in self.tokens:
            for name, value in self.tokens["spacing"].items():
                css_lines.append(f"  --spacing-{name}: {value};")
        
        # 字体变量
        if "typography" in self.tokens:
            typography = self.tokens["typography"]
            if "fontSize" in typography:
                for name, value in typography["fontSize"].items():
                    css_lines.append(f"  --font-size-{name}: {value};")
        
        # 圆角变量
        if "borders" in self.tokens and "radius" in self.tokens["borders"]:
            for name, value in self.tokens["borders"]["radius"].items():
                css_lines.append(f"  --radius-{name}: {value};")
        
        css_lines.append("}")
        
        return '\n'.join(css_lines)
    
    def create_component_variant(
        self,
        component_name: str,
        variant_name: str,
        style_overrides: Dict[str, str]
    ) -> Dict:
        """创建组件变体"""
        variants = self._load_variants()
        
        if component_name not in variants:
            variants[component_name] = {}
        
        variants[component_name][variant_name] = {
            "style_overrides": style_overrides,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_variants(variants)
        
        return {
            "component": component_name,
            "variant": variant_name,
            "overrides": style_overrides
        }
    
    def get_component_variants(self, component_name: str) -> Dict:
        """获取组件的所有变体"""
        variants = self._load_variants()
        return variants.get(component_name, {})
    
    def delete_component_variant(
        self, 
        component_name: str, 
        variant_name: str
    ) -> Dict:
        """删除组件变体"""
        variants = self._load_variants()
        
        if component_name not in variants:
            return {"error": f"Component '{component_name}' not found"}
        
        if variant_name not in variants[component_name]:
            return {"error": f"Variant '{variant_name}' not found"}
        
        deleted = variants[component_name].pop(variant_name)
        self._save_variants(variants)
        
        return {
            "component": component_name,
            "variant": variant_name,
            "deleted": deleted
        }
    
    def validate_tokens(self) -> List[Dict]:
        """验证设计 tokens 的一致性"""
        issues = []
        
        # 检查颜色格式
        if "colors" in self.tokens:
            for color_name, shades in self.tokens["colors"].items():
                if isinstance(shades, dict):
                    for shade, value in shades.items():
                        if not self._is_valid_color(value):
                            issues.append({
                                "type": "invalid_color",
                                "token": f"colors.{color_name}.{shade}",
                                "value": value,
                                "message": f"Invalid color format: {value}"
                            })
        
        # 检查间距值
        if "spacing" in self.tokens:
            for name, value in self.tokens["spacing"].items():
                if not self._is_valid_spacing(value):
                    issues.append({
                        "type": "invalid_spacing",
                        "token": f"spacing.{name}",
                        "value": value,
                        "message": f"Invalid spacing value: {value}"
                    })
        
        return issues
    
    def reset_to_defaults(self) -> Dict:
        """重置为默认 tokens"""
        self.tokens = self.DEFAULT_TOKENS.copy()
        self._save_tokens()
        
        return {
            "message": "Design tokens reset to defaults",
            "timestamp": datetime.now().isoformat()
        }
    
    def _load_variants(self) -> Dict:
        """加载组件变体"""
        if self.variants_file.exists():
            with open(self.variants_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_variants(self, variants: Dict):
        """保存组件变体"""
        with open(self.variants_file, 'w', encoding='utf-8') as f:
            json.dump(variants, f, indent=2, ensure_ascii=False)
    
    def _is_valid_color(self, value: str) -> bool:
        """验证颜色格式"""
        # 支持 hex、rgb、hsl
        patterns = [
            r'^#[0-9A-Fa-f]{3}$',
            r'^#[0-9A-Fa-f]{6}$',
            r'^#[0-9A-Fa-f]{8}$',
            r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$',
            r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$',
            r'^hsl\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)$',
        ]
        
        import re
        for pattern in patterns:
            if re.match(pattern, value):
                return True
        
        return False
    
    def _is_valid_spacing(self, value: str) -> bool:
        """验证间距值格式"""
        # 支持 rem、px、em、%
        import re
        return bool(re.match(r'^[\d.]+(rem|px|em|%)$', value))

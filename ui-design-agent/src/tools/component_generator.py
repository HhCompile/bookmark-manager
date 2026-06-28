#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件生成器
根据描述生成 React + Tailwind 组件
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ComponentGenerator:
    """UI 组件生成器"""
    
    # 组件模板
    COMPONENT_TEMPLATE = '''import { useState } from 'react'
import { motion } from 'motion/react'

interface {component_name}Props {{
{props_interface}
}}

/**
 * {component_name} 组件
 * {description}
 */
export default function {component_name}({{
{props_destructure}
}}: {component_name}Props) {{
  {state_hooks}
  
  return (
    {jsx_content}
  )
}}
'''
    
    # 常用图标映射
    ICON_IMPORTS = {
        'search': 'Search',
        'user': 'User',
        'settings': 'Settings',
        'menu': 'Menu',
        'close': 'X',
        'check': 'Check',
        'plus': 'Plus',
        'trash': 'Trash2',
        'edit': 'Pencil',
        'eye': 'Eye',
        'heart': 'Heart',
        'star': 'Star',
        'bell': 'Bell',
        'calendar': 'Calendar',
        'clock': 'Clock',
        'home': 'Home',
        'folder': 'Folder',
        'file': 'FileText',
        'link': 'Link',
        'tag': 'Tag',
        'filter': 'Filter',
        'sort': 'ArrowUpDown',
        'refresh': 'RefreshCw',
        'upload': 'Upload',
        'download': 'Download',
        'share': 'Share2',
        'more': 'MoreHorizontal',
        'back': 'ArrowLeft',
        'forward': 'ArrowRight',
        'up': 'ArrowUp',
        'down': 'ArrowDown',
    }
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontend_root = self.project_root / "bookmark-manager-web"
        self.components_dir = self.frontend_root / "src" / "components"
    
    def generate_component(
        self, 
        description: str, 
        component_name: Optional[str] = None,
        props: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """根据描述生成组件"""
        
        # 如果没有提供组件名，从描述中提取
        if not component_name:
            component_name = self._extract_component_name_from_description(description)
        
        # 分析描述，提取组件特性
        features = self._analyze_description(description)
        
        # 生成 props
        if not props:
            props = self._generate_props(features)
        
        # 生成代码
        code = self._generate_code(component_name, description, features, props)
        
        # 保存文件
        file_path = self._save_component(component_name, code)
        
        return {
            "component_name": component_name,
            "file_path": str(file_path.relative_to(self.frontend_root)),
            "code": code,
            "features": features,
            "props": props
        }
    
    def generate_style_variant(
        self,
        component_name: str,
        variant_name: str,
        style_changes: Dict[str, str]
    ) -> Dict[str, Any]:
        """为现有组件生成样式变体"""
        
        original_path = self.components_dir / f"{component_name}.tsx"
        if not original_path.exists():
            return {"error": f"组件 {component_name} 不存在"}
        
        original_code = original_path.read_text(encoding='utf-8')
        
        # 应用样式变更
        variant_code = self._apply_style_changes(original_code, style_changes)
        
        # 保存变体
        variant_file_name = f"{component_name}{variant_name}.tsx"
        variant_path = self.components_dir / "variants" / variant_file_name
        variant_path.parent.mkdir(parents=True, exist_ok=True)
        variant_path.write_text(variant_code, encoding='utf-8')
        
        return {
            "original": str(original_path.relative_to(self.frontend_root)),
            "variant": str(variant_path.relative_to(self.frontend_root)),
            "changes": style_changes
        }
    
    def _extract_component_name_from_description(self, description: str) -> str:
        """从描述中提取组件名"""
        # 提取关键词
        keywords = []
        
        # 常见组件类型
        component_types = [
            'button', 'card', 'modal', 'dialog', 'input', 'form',
            'list', 'table', 'nav', 'header', 'footer', 'sidebar',
            'dropdown', 'select', 'tabs', 'accordion', 'tooltip',
            'badge', 'avatar', 'alert', 'toast', 'popover'
        ]
        
        desc_lower = description.lower()
        for comp_type in component_types:
            if comp_type in desc_lower:
                keywords.append(comp_type.capitalize())
        
        # 功能关键词
        function_keywords = {
            'search': 'Search',
            'filter': 'Filter',
            'sort': 'Sort',
            'upload': 'Upload',
            'download': 'Download',
            'create': 'Create',
            'edit': 'Edit',
            'delete': 'Delete',
            'view': 'View',
            'preview': 'Preview',
            'confirm': 'Confirm',
            'notification': 'Notification',
        }
        
        for keyword, suffix in function_keywords.items():
            if keyword in desc_lower:
                keywords.append(suffix)
        
        if keywords:
            return ''.join(keywords)
        
        return "GeneratedComponent"
    
    def _analyze_description(self, description: str) -> Dict[str, Any]:
        """分析组件描述"""
        desc_lower = description.lower()
        
        features = {
            "has_icon": any(icon in desc_lower for icon in self.ICON_IMPORTS.keys()),
            "has_animation": any(word in desc_lower for word in ['动画', 'animation', 'transition', 'motion']),
            "has_state": any(word in desc_lower for word in ['状态', 'state', 'loading', 'disabled']),
            "has_interaction": any(word in desc_lower for word in ['点击', 'hover', 'focus', '交互']),
            "is_form": any(word in desc_lower for word in ['表单', 'form', 'input']),
            "is_list": any(word in desc_lower for word in ['列表', 'list', 'table']),
            "is_modal": any(word in desc_lower for word in ['弹窗', 'modal', 'dialog', '抽屉', 'drawer']),
            "style_variant": self._detect_style_variant(desc_lower),
            "icons": [self.ICON_IMPORTS[k] for k in self.ICON_IMPORTS if k in desc_lower],
        }
        
        return features
    
    def _detect_style_variant(self, description: str) -> str:
        """检测样式变体"""
        variants = {
            'primary': ['主要', 'primary', '主色'],
            'secondary': ['次要', 'secondary', '次要色'],
            'outline': ['描边', 'outline', '边框'],
            'ghost': ['幽灵', 'ghost', '透明'],
            'glass': ['玻璃', 'glass', '拟态', 'glassmorphism'],
            'neumorphism': ['新拟态', 'neumorphism'],
            'flat': ['扁平', 'flat'],
            'gradient': ['渐变', 'gradient'],
        }
        
        for variant, keywords in variants.items():
            if any(kw in description for kw in keywords):
                return variant
        
        return 'default'
    
    def _generate_props(self, features: Dict) -> List[Dict]:
        """生成 props 定义"""
        props = []
        
        # 基础 props
        props.append({"name": "className", "type": "string", "optional": True, "default": "''"})
        
        # 根据特性添加 props
        if features.get('has_icon'):
            props.append({"name": "icon", "type": "React.ElementType", "optional": True})
        
        if features.get('is_form'):
            props.append({"name": "value", "type": "string", "optional": True})
            props.append({"name": "onChange", "type": "(value: string) => void", "optional": True})
            props.append({"name": "placeholder", "type": "string", "optional": True})
        
        if features.get('has_state'):
            props.append({"name": "isLoading", "type": "boolean", "optional": True, "default": "false"})
            props.append({"name": "isDisabled", "type": "boolean", "optional": True, "default": "false"})
        
        if features.get('has_interaction'):
            props.append({"name": "onClick", "type": "() => void", "optional": True})
        
        if features.get('is_list'):
            props.append({"name": "items", "type": "any[]", "optional": False})
        
        if features.get('is_modal'):
            props.append({"name": "isOpen", "type": "boolean", "optional": False})
            props.append({"name": "onClose", "type": "() => void", "optional": False})
        
        return props
    
    def _generate_code(
        self, 
        component_name: str, 
        description: str,
        features: Dict,
        props: List[Dict]
    ) -> str:
        """生成组件代码"""
        
        # 生成 imports
        imports = self._generate_imports(features)
        
        # 生成 interface
        props_interface = self._generate_props_interface(props)
        
        # 生成 props 解构
        props_destructure = self._generate_props_destructure(props)
        
        # 生成 state hooks
        state_hooks = self._generate_state_hooks(features)
        
        # 生成 JSX
        jsx_content = self._generate_jsx(component_name, features, props)
        
        # 组合代码
        code = f"""{imports}

interface {component_name}Props {{
{props_interface}
}}

/**
 * {component_name} 组件
 * {description}
 * 
 * @generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */
export default function {component_name}({{
{props_destructure}
}}: {component_name}Props) {{
  {state_hooks}
  
  return (
{jsx_content}
  )
}}
"""
        
        return code
    
    def _generate_imports(self, features: Dict) -> str:
        """生成 import 语句"""
        imports = ["import { useState } from 'react'"]
        
        if features.get('has_animation'):
            imports.append("import { motion } from 'motion/react'")
        
        if features.get('icons'):
            icons_str = ', '.join(set(features['icons']))
            imports.append(f"import {{ {icons_str} }} from 'lucide-react'")
        
        return '\n'.join(imports)
    
    def _generate_props_interface(self, props: List[Dict]) -> str:
        """生成 props interface"""
        lines = []
        for prop in props:
            optional = '?' if prop.get('optional') else ''
            lines.append(f"  {prop['name']}{optional}: {prop['type']}")
        return '\n'.join(lines) if lines else '  // 无 props'
    
    def _generate_props_destructure(self, props: List[Dict]) -> str:
        """生成 props 解构"""
        lines = []
        for prop in props:
            if 'default' in prop:
                lines.append(f"  {prop['name']} = {prop['default']},")
            else:
                lines.append(f"  {prop['name']},")
        return '\n'.join(lines) if lines else '  // 无 props'
    
    def _generate_state_hooks(self, features: Dict) -> str:
        """生成 state hooks"""
        hooks = []
        
        if features.get('has_state'):
            hooks.append("const [isActive, setIsActive] = useState(false)")
        
        if features.get('is_form'):
            hooks.append("const [inputValue, setInputValue] = useState('')")
        
        return '\n  '.join(hooks) if hooks else "// 无状态"
    
    def _generate_jsx(self, component_name: str, features: Dict, props: List[Dict]) -> str:
        """生成 JSX"""
        variant = features.get('style_variant', 'default')
        
        # 基础样式类
        base_classes = self._get_base_classes(variant)
        
        # 根据组件类型生成不同结构
        if features.get('is_modal'):
            return self._generate_modal_jsx(component_name, features, base_classes)
        elif features.get('is_list'):
            return self._generate_list_jsx(component_name, features, base_classes)
        elif features.get('is_form'):
            return self._generate_form_jsx(component_name, features, base_classes)
        else:
            return self._generate_default_jsx(component_name, features, base_classes)
    
    def _get_base_classes(self, variant: str) -> str:
        """获取基础样式类"""
        classes = {
            'default': 'bg-white border border-gray-200 rounded-lg p-4',
            'primary': 'bg-blue-600 text-white rounded-lg p-4',
            'secondary': 'bg-gray-100 text-gray-900 rounded-lg p-4',
            'outline': 'bg-transparent border-2 border-blue-500 text-blue-600 rounded-lg p-4',
            'ghost': 'bg-transparent hover:bg-gray-100 text-gray-700 rounded-lg p-4',
            'glass': 'bg-white/70 backdrop-blur-md border border-white/20 rounded-lg p-4 shadow-lg',
            'gradient': 'bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg p-4',
        }
        return classes.get(variant, classes['default'])
    
    def _generate_default_jsx(self, component_name: str, features: Dict, base_classes: str) -> str:
        """生成默认 JSX"""
        wrapper = "motion.div" if features.get('has_animation') else "div"
        animation_props = """
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}""" if features.get('has_animation') else ""
        
        return f'''    <{wrapper}
      className={{`{base_classes} ${{className}}`}}{animation_props}
    >
      {features.get('icons') and features['icons'][0] and f'<{features["icons"][0]} className="w-5 h-5" />' or '<!-- 组件内容 -->'}
      <span>{component_name}</span>
    </{wrapper}>'''
    
    def _generate_modal_jsx(self, component_name: str, features: Dict, base_classes: str) -> str:
        """生成模态框 JSX"""
        return f'''    <>
      {{isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="{base_classes} w-full max-w-md mx-4"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">{component_name}</h3>
              <button onClick={{onClose}} className="p-1 hover:bg-gray-100 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div>{{/* 内容区域 */}}</div>
          </motion.div>
        </div>
      )}}
    </>'''
    
    def _generate_list_jsx(self, component_name: str, features: Dict, base_classes: str) -> str:
        """生成列表 JSX"""
        return f'''    <div className={{`{base_classes} ${{className}}`}}>
      {{items?.map((item, index) => (
        <div
          key={{index}}
          className="flex items-center justify-between py-3 border-b last:border-b-0 border-gray-100"
        >
          <span>{{item}}</span>
        </div>
      ))}}
    </div>'''
    
    def _generate_form_jsx(self, component_name: str, features: Dict, base_classes: str) -> str:
        """生成表单 JSX"""
        return f'''    <div className={{`{base_classes} ${{className}}`}}>
      <input
        type="text"
        value={{value}}
        placeholder={{placeholder}}
        onChange={{(e) => onChange?.(e.target.value)}}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>'''
    
    def _apply_style_changes(self, code: str, style_changes: Dict[str, str]) -> str:
        """应用样式变更"""
        modified_code = code
        
        for pattern, replacement in style_changes.items():
            # 支持正则替换
            if pattern.startswith('regex:'):
                regex_pattern = pattern[6:]
                modified_code = re.sub(regex_pattern, replacement, modified_code)
            else:
                # 简单字符串替换
                modified_code = modified_code.replace(pattern, replacement)
        
        return modified_code
    
    def _save_component(self, component_name: str, code: str) -> Path:
        """保存组件文件"""
        file_path = self.components_dir / f"{component_name}.tsx"
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        file_path.write_text(code, encoding='utf-8')
        
        return file_path

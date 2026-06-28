#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Design Agent - MCP Server
智能 UI 设计助手的 MCP 服务器实现
"""

import json
import sys
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.ui_analyzer import UIAnalyzer
from src.tools.component_generator import ComponentGenerator
from src.tools.style_modifier import StyleModifier
from src.tools.design_system_manager import DesignSystemManager


class UIDesignMCPServer:
    """
    UI Design Agent MCP 服务器
    提供 UI 分析、组件生成、样式修改等工具
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.analyzer = UIAnalyzer(self.project_root)
        self.generator = ComponentGenerator(self.project_root)
        self.modifier = StyleModifier(self.project_root)
        self.design_system = DesignSystemManager(self.project_root)
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理 MCP 请求"""
        method = request.get("method")
        params = request.get("params", {})
        
        handlers = {
            "analyze_component": self._handle_analyze_component,
            "generate_component": self._handle_generate_component,
            "modify_style": self._handle_modify_style,
            "update_design_token": self._handle_update_design_token,
            "list_components": self._handle_list_components,
            "extract_design_tokens": self._handle_extract_design_tokens,
            "suggest_improvements": self._handle_suggest_improvements,
        }
        
        handler = handlers.get(method)
        if handler:
            try:
                result = handler(params)
                return {
                    "status": "success",
                    "result": result
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }
        else:
            return {
                "status": "error",
                "error": f"Unknown method: {method}"
            }
    
    def _handle_analyze_component(self, params: Dict) -> Dict:
        """分析组件"""
        file_path = params.get("file_path")
        return self.analyzer.analyze_component(file_path)
    
    def _handle_generate_component(self, params: Dict) -> Dict:
        """生成组件"""
        description = params.get("description")
        component_name = params.get("component_name")
        props = params.get("props", [])
        return self.generator.generate_component(description, component_name, props)
    
    def _handle_modify_style(self, params: Dict) -> Dict:
        """修改样式"""
        file_path = params.get("file_path")
        style_changes = params.get("style_changes", {})
        return self.modifier.modify_style(file_path, style_changes)
    
    def _handle_update_design_token(self, params: Dict) -> Dict:
        """更新设计 token"""
        token_type = params.get("token_type")
        token_name = params.get("token_name")
        token_value = params.get("token_value")
        return self.design_system.update_token(token_type, token_name, token_value)
    
    def _handle_list_components(self, params: Dict) -> List[Dict]:
        """列出项目中的组件"""
        directory = params.get("directory", "src/components")
        return self.analyzer.list_components(directory)
    
    def _handle_extract_design_tokens(self, params: Dict) -> Dict:
        """提取设计 tokens"""
        return self.analyzer.extract_design_tokens()
    
    def _handle_suggest_improvements(self, params: Dict) -> List[Dict]:
        """提供改进建议"""
        file_path = params.get("file_path")
        return self.analyzer.suggest_improvements(file_path)


def main():
    """MCP 服务器主入口"""
    server = UIDesignMCPServer()
    
    # 读取标准输入
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            request = json.loads(line)
            response = server.handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "status": "error",
                "error": f"Invalid JSON: {e}"
            }), flush=True)
        except Exception as e:
            print(json.dumps({
                "status": "error", 
                "error": str(e)
            }), flush=True)


if __name__ == "__main__":
    main()

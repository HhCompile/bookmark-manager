#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bookmark Manager 统一启动脚本

启动顺序：
1. 后端 admin (Flask, 端口 9001)
2. 前端 web (React/Vite, 端口 3000)

特性：
- 端口冲突检测（启动前先 ping）
- 后端健康检查（GET /v1/bookmarks/stats）
- 跨平台（macOS / Linux / Windows）
- 流式输出 + 彩色标识
- Ctrl+C 干净退出（关闭所有子进程）

使用：python3 start.py
"""
from __future__ import annotations

import os
import sys
import time
import signal
import socket
import platform
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List


# ============================================================================
# 配置
# ============================================================================

BACKEND_DIR = "bookmark-manager-admin"
FRONTEND_DIR = "bookmark-manager-web"
BACKEND_PORT = 9001  # Flask (legacy, 已废弃，保留兼容)
FRONTEND_PORT = 3000
FASTAPI_PORT = 9002
FASTAPI_ENABLED = os.environ.get("V2_ENABLED", "true").lower() != "false"
FLASK_ENABLED = os.environ.get("FLASK_ENABLED", "false").lower() == "true"  # 默认关闭

HEALTH_CHECK_TIMEOUT = 5  # 后端启动后等多久算超时
BACKEND_STARTUP_DELAY = 2  # 启动后端后等几秒


# ============================================================================
# 颜色（Windows 自动禁用）
# ============================================================================

class C:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    DIM = '\033[2m'
    END = '\033[0m'


if platform.system() == "Windows":
    for attr in dir(C):
        if not attr.startswith('_') and attr != 'END':
            setattr(C, attr, '')


# ============================================================================
# 数据模型
# ============================================================================

@dataclass(frozen=True)
class ServiceConfig:
    """单个服务的启动配置（不可变）"""
    name: str           # "后端" / "前端"
    dir: str            # 相对路径
    port: int           # 监听端口
    color: str          # 输出标识色
    venv_subdirs: tuple # 虚拟环境子目录（(bin/Scripts, activate)）


BACKEND = ServiceConfig(
    name="后端",
    dir=BACKEND_DIR,
    port=BACKEND_PORT,
    color=C.BLUE,
    venv_subdirs=(
        ("bin", "activate"),       # Unix
        ("Scripts", "activate.bat"),  # Windows
    ),
)

FRONTEND = ServiceConfig(
    name="前端",
    dir=FRONTEND_DIR,
    port=FRONTEND_PORT,
    color=C.GREEN,
    venv_subdirs=(),  # 前端不用 venv
)

# FastAPI v2（可选：V2_ENABLED=false 可关）
@dataclass(frozen=True)
class FastAPIConfig:
    name: str = "FastAPI"
    dir: str = BACKEND_DIR
    port: int = FASTAPI_PORT
    color: str = C.CYAN
    entrypoint: str = "app_v2/main.py"


FASTAPI = FastAPIConfig()


# ============================================================================
# 工具函数
# ============================================================================

def log(msg: str, color: str = C.END) -> None:
    """彩色打印"""
    print(f"{color}{msg}{C.END}")


def is_port_in_use(port: int) -> bool:
    """检测端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def check_port_available(port: int, service: str) -> bool:
    """启动前检查端口可用性"""
    if is_port_in_use(port):
        log(f"⚠️  端口 {port} 已被占用（{service} 需要此端口）", C.YELLOW)
        log(f"   提示：lsof -nP -iTCP:{port} -sTCP:LISTEN  查看占用进程", C.DIM)
        return False
    return True


def find_venv_python(backend_path: Path) -> Optional[List[str]]:
    """找到虚拟环境的 python 解释器和激活方式"""
    for subdir, activate in BACKEND.venv_subdirs:
        activate_path = backend_path / "venv_new" / subdir / activate
        if activate_path.exists():
            return ["bash", "-c", f"source '{activate_path}' && python3 run.py"] \
                if platform.system() != "Windows" else \
                ["cmd", "/c", f"call {activate_path} && python run.py"]

        # 兼容老的 venv 名字
        activate_path = backend_path / "venv" / subdir / activate
        if activate_path.exists():
            return ["bash", "-c", f"source '{activate_path}' && python3 run.py"] \
                if platform.system() != "Windows" else \
                ["cmd", "/c", f"call {activate_path} && python run.py"]

    return None  # 找不到 venv


def wait_for_health(url: str, timeout: int = HEALTH_CHECK_TIMEOUT) -> bool:
    """轮询 HTTP 端点直到返回 200 或超时"""
    import urllib.request
    import urllib.error

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(0.3)
    return False


# ============================================================================
# 进程管理
# ============================================================================

processes: List[subprocess.Popen] = []
_lock = threading.Lock()


def cleanup(signum=None, frame=None) -> None:
    """清理所有子进程（含 Flask debug reloader 启的子进程）"""
    log("\n🛑 正在关闭服务...", C.YELLOW)

    with _lock:
        for proc in processes:
            if proc.poll() is None:
                # 杀整个进程组（包含 Flask reloader 等衍生的子进程）
                try:
                    if platform.system() != "Windows":
                        os.killpg(proc.pid, signal.SIGTERM)
                    else:
                        proc.terminate()
                except (ProcessLookupError, PermissionError):
                    proc.terminate()

                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if platform.system() != "Windows":
                        try:
                            os.killpg(proc.pid, signal.SIGKILL)
                        except (ProcessLookupError, PermissionError):
                            pass
                    else:
                        proc.kill()

    log("✅ 所有服务已关闭", C.GREEN)
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def stream_output(proc: subprocess.Popen, prefix: str, color: str) -> None:
    """流式输出进程日志"""
    try:
        for line in iter(proc.stdout.readline, ''):
            print(f"{color}[{prefix}]{C.END} {line.rstrip()}")
    except (ValueError, OSError):
        pass  # 进程已结束


def start_service(cfg: ServiceConfig) -> Optional[subprocess.Popen]:
    """启动单个服务"""
    log(f"▶ 启动{cfg.name}服务...", cfg.color)

    svc_path = Path(cfg.dir).resolve()
    if not svc_path.exists():
        log(f"❌ 找不到目录: {cfg.dir}", C.RED)
        return None

    # 构建命令
    if cfg is BACKEND:
        cmd = find_venv_python(svc_path)
        if cmd is None:
            log("⚠️  未检测到虚拟环境，使用系统 python", C.YELLOW)
            cmd = ["python3", "run.py"] if platform.system() != "Windows" else ["python", "run.py"]
    else:  # FRONTEND
        # pnpm 优先，回退 npm
        try:
            subprocess.run(["pnpm", "--version"], capture_output=True, check=True, timeout=3)
            cmd = ["pnpm", "dev"]
            log("  使用 pnpm", C.DIM)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            cmd = ["npm", "run", "dev"]
            log("  使用 npm（pnpm 未安装）", C.DIM)

    log(f"  命令: {' '.join(cmd)}", C.DIM)
    log(f"  目录: {svc_path}", C.DIM)

    proc = subprocess.Popen(
        cmd,
        cwd=svc_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        # macOS/Linux: 启动新会话，cleanup 时可以杀整个进程组
        # （包括 Flask debug reloader 衍生的子进程）
        start_new_session=(platform.system() != "Windows"),
    )

    return proc


# ============================================================================
# 主流程
# ============================================================================

def main() -> int:
    log("=" * 50, C.CYAN)
    log("  Bookmark Manager 一键启动脚本", C.CYAN)
    log("=" * 50, C.CYAN)
    print()

    # === 1. 端口检查 ===
    log("🔍 端口检查...", C.CYAN)
    backend_ok = check_port_available(BACKEND_PORT, "Flask (legacy)") if FLASK_ENABLED else True
    frontend_ok = check_port_available(FRONTEND_PORT, "前端 web")
    fastapi_ok = check_port_available(FASTAPI_PORT, "FastAPI v2") if FASTAPI_ENABLED else True
    print()

    if not backend_ok and not frontend_ok and not fastapi_ok:
        log("❌ 三个端口都已被占用，请先关闭现有服务", C.RED)
        return 1

    # === 2. 启动后端 (Flask，默认关闭) ===
    backend_proc = None
    if FLASK_ENABLED:
        backend_proc = start_service(BACKEND)
        if backend_proc is None:
            log("❌ Flask 后端启动失败", C.RED)
            return 1
        processes.append(backend_proc)
        log(f"✅ Flask 进程已启动 (PID: {backend_proc.pid})", C.GREEN)
    else:
        log("ℹ️  Flask :9001 未启用（FLASK_ENABLED=true 启动）", C.DIM)
    if backend_proc is None:
        log("❌ 后端启动失败", C.RED)
        return 1

    processes.append(backend_proc)
    log(f"✅ 后端进程已启动 (PID: {backend_proc.pid})", C.GREEN)

    # === 3. 等后端健康 ===
    log("⏳ 等待后端健康检查...", C.YELLOW)
    if wait_for_health(f"http://127.0.0.1:{BACKEND_PORT}/v1/bookmarks/stats", HEALTH_CHECK_TIMEOUT):
        log(f"✅ 后端就绪: http://localhost:{BACKEND_PORT}", C.GREEN)
    else:
        log(f"⚠️  后端健康检查超时（{HEALTH_CHECK_TIMEOUT}s），但进程在跑", C.YELLOW)
    print()

    # === 4. 启动前端 ===
    frontend_proc = start_service(FRONTEND)
    if frontend_proc:
        processes.append(frontend_proc)
        log(f"✅ 前端进程已启动 (PID: {frontend_proc.pid})", C.GREEN)
    print()

    # === 4.5 启动 FastAPI v2（可选，默认开启）===
    fastapi_proc = None
    if FASTAPI_ENABLED and fastapi_ok:
        log("▶ 启动 FastAPI v2...", FASTAPI.color)
        fastapi_cmd = [
            sys.executable,
            os.path.join(BACKEND_DIR, FASTAPI.entrypoint),
        ]
        log(f"  命令: {' '.join(fastapi_cmd)}", C.DIM)
        fastapi_proc = subprocess.Popen(
            fastapi_cmd,
            cwd=os.path.abspath(BACKEND_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        processes.append(fastapi_proc)
        log(f"✅ FastAPI v2 进程已启动 (PID: {fastapi_proc.pid})", FASTAPI.color)

        # 等 FastAPI 健康检查（给更长超时：uvicorn 启动比 Flask reloader 慢）
        if wait_for_health(f"http://127.0.0.1:{FASTAPI_PORT}/health", HEALTH_CHECK_TIMEOUT * 2):
            log(f"✅ FastAPI 就绪: http://localhost:{FASTAPI_PORT}", FASTAPI.color)
            log(f"   文档: http://localhost:{FASTAPI_PORT}/docs", C.DIM)
        else:
            log(f"⚠️  FastAPI 健康检查超时（10s），但进程在跑，访问 :9002/docs", C.YELLOW)
        print()
    elif not FASTAPI_ENABLED:
        log("ℹ️  FastAPI v2 未启用（V2_ENABLED=false）", C.DIM)
    print()

    # === 5. 流式输出（后台线程） ===
    log("=" * 50, C.CYAN)
    log("  📚 所有服务已启动！", C.CYAN)
    log("=" * 50, C.CYAN)
    print()
    log(f"  前端: {C.BLUE}http://localhost:{FRONTEND_PORT}{C.END}", C.END)
    if FLASK_ENABLED:
        log(f"  Flask (legacy):{C.GREEN}http://localhost:{BACKEND_PORT}{C.END}", C.END)
    if FASTAPI_ENABLED and fastapi_proc:
        log(f"  FastAPI v2:    {FASTAPI.color}http://localhost:{FASTAPI_PORT}{C.END}", C.END)
        log(f"  FastAPI 文档:  {FASTAPI.color}http://localhost:{FASTAPI_PORT}/docs{C.END}", C.END)
    print()
    log("  按 Ctrl+C 停止所有服务", C.YELLOW)
    print()

    if backend_proc:
        t = threading.Thread(target=stream_output, args=(backend_proc, "Flask", C.BLUE), daemon=True)
        t.start()

    if frontend_proc:
        t = threading.Thread(target=stream_output, args=(frontend_proc, "前端", C.GREEN), daemon=True)
        t.start()

    if fastapi_proc:
        t = threading.Thread(target=stream_output, args=(fastapi_proc, "FastAPI", FASTAPI.color), daemon=True)
        t.start()

    # === 6. 主循环 ===
    try:
        while processes:
            with _lock:
                for proc in processes[:]:
                    if proc.poll() is not None:
                        processes.remove(proc)
                        log(f"⚠️  进程退出（returncode={proc.returncode}）", C.YELLOW)
            time.sleep(0.5)
    except KeyboardInterrupt:
        cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
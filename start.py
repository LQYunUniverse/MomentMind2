#!/usr/bin/env python3
"""
MomentMind 启动脚本
快速启动和配置检查工具
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查Python依赖是否已安装"""
    print("🔍 检查Python依赖...")
    try:
        import fastapi
        import uvicorn
        import openai
        import requests
        import dotenv
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("💡 请运行: pip install -r requirements.txt")
        return False

def check_env_config():
    """检查环境变量配置"""
    print("\n🔍 检查环境变量配置...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ 未找到 .env 文件")
        print("💡 请复制 env.example 为 .env 并填入您的配置")
        return False
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "AZURE_OPENAI_KEY_CHAT",
        "AZURE_OPENAI_KEY_IMAGE",
        "AZURE_OPENAI_ENDPOINT_CHAT", 
        "AZURE_OPENAI_DEPLOYMENT_CHAT",
        "AZURE_OPENAI_ENDPOINT_IMAGE",
        "AZURE_OPENAI_DEPLOYMENT_IMAGE"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("💡 请在 .env 文件中配置这些变量")
        return False
    
    print("✅ 环境变量配置完整")
    return True

def create_static_dir():
    """确保静态文件目录存在"""
    static_dir = Path("static")
    if not static_dir.exists():
        print("📁 创建静态文件目录...")
        static_dir.mkdir()
    
    # 检查静态文件是否存在
    required_files = ["index.html", "app.js"]
    for file in required_files:
        if not (static_dir / file).exists():
            print(f"❌ 缺少静态文件: static/{file}")
            return False
    
    print("✅ 静态文件准备就绪")
    return True

def start_server():
    """启动FastAPI服务器"""
    print("\n🚀 启动MomentMind服务器...")
    
    port = os.getenv("PORT", "8787")
    
    print(f"📡 服务器将在 http://localhost:{port} 启动")
    print("🌟 打开浏览器访问上述地址开始使用MomentMind")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=int(port),
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 MomentMind服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🧠 MomentMind - 多模态捕获和AI增强系统")
    print("=" * 50)
    
    # 检查各项配置
    if not check_dependencies():
        sys.exit(1)
    
    if not check_env_config():
        sys.exit(1)
        
    if not create_static_dir():
        sys.exit(1)
    
    print("\n✨ 所有检查通过，准备启动服务器...")
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()

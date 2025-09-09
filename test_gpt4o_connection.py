#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GPT-4o部署连接
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

def test_gpt4o_connection():
    """测试GPT-4o连接"""
    load_dotenv()
    
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION_CHAT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_CHAT")
        )
        
        print("🔗 正在测试GPT-4o连接...")
        print(f"📍 Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT_CHAT')}")
        print(f"🚀 Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT_CHAT')}")
        print(f"📅 API Version: {os.getenv('AZURE_OPENAI_API_VERSION_CHAT')}")
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_CHAT"),
            messages=[
                {"role": "user", "content": "Hello! 请简单介绍一下你的图片分析能力。"}
            ],
            max_tokens=150
        )
        
        print("\n✅ GPT-4o连接成功！")
        print(f"🤖 AI回复: {response.choices[0].message.content}")
        
        # 测试是否支持图片
        print("\n🖼️ 测试图片分析功能...")
        vision_response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_CHAT"),
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "这是一个测试，你支持图片分析吗？"}
                    ]
                }
            ],
            max_tokens=100
        )
        
        print(f"✅ 图片分析功能可用: {vision_response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n💡 可能的原因:")
        print("1. gpt-4o模型尚未部署")
        print("2. 部署名称不匹配")
        print("3. API版本不兼容")
        print("4. 密钥或端点配置错误")

if __name__ == "__main__":
    test_gpt4o_connection()

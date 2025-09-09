#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GPT-4o真实图片分析能力
"""

import os
import base64
from openai import AzureOpenAI
from dotenv import load_dotenv

def test_vision_with_base64():
    """使用base64编码的图片测试视觉功能"""
    load_dotenv()
    
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION_CHAT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_CHAT")
        )
        
        # 创建一个简单的base64图片（1x1像素的红色图片）
        # 这是一个有效的PNG图片的base64编码
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        print("🧪 测试真实图片分析功能...")
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_CHAT"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请描述这张图片中的内容。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{test_image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=200
        )
        
        print("✅ 图片分析测试成功！")
        print(f"🤖 AI分析结果: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ 图片分析测试失败: {e}")
        if "vision" in str(e).lower() or "image" in str(e).lower():
            print("💡 此GPT-4o部署不支持视觉功能")
        return False

if __name__ == "__main__":
    success = test_vision_with_base64()
    if success:
        print("\n🎉 恭喜！GPT-4o支持图片分析")
    else:
        print("\n❌ GPT-4o不支持图片分析，建议:")
        print("1. 检查Azure部署配置")
        print("2. 尝试部署gpt-4o-mini")
        print("3. 或使用gpt-4-vision-preview")

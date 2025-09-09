#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试灵感分析功能
"""

import requests
import json

def test_inspiration_analysis():
    """测试灵感分析是否返回详细分析"""
    url = "http://localhost:8790/api/summarize_inspiration"
    
    test_data = {
        "text": "我很喜欢牛油果的绿色质感，想要设计一个简约的包装",
        "context": "为健康食品品牌设计包装",
        "recording_method": "text"
    }
    
    print("🧪 测试灵感分析功能...")
    print(f"📝 输入文本: {test_data['text']}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 请求成功")
            
            # 检查返回的分析内容
            summary = result.get('summary', '')
            
            print(f"\n📊 返回内容长度: {len(summary)} 字符")
            print(f"🧠 记忆状态: {result.get('memory_status', {})}")
            
            print("\n📝 分析结果:")
            print("=" * 50)
            print(summary)
            print("=" * 50)
            
            # 检查是否包含关键词分析
            if '关键词' in summary or '核心概念' in summary or '灵感脉络' in summary:
                print("\n✅ 包含详细分析内容")
            else:
                print("\n❌ 缺少详细分析内容")
                
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求出错: {e}")

if __name__ == "__main__":
    test_inspiration_analysis()

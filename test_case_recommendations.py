#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的案例推荐功能
"""

import requests
import json

def test_case_recommendations():
    """测试案例推荐功能"""
    url = "http://localhost:8787/api/get_case_recommendations"
    
    test_cases = [
        "我喜欢牛油果的绿色质感",
        "玻璃材质的透明设计",
        "集市里规整的摊位布局",
        "简约的包装设计风格"
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"测试案例 {i}: {test_text}")
        print('='*50)
        
        try:
            response = requests.post(url, json={"inspiration_text": test_text}, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 请求成功")
                print(f"📊 关联历史灵感数量: {result.get('related_inspirations_count', 0)}")
                print(f"🌐 真实案例数量: {result.get('real_cases_count', 0)}")
                print("\n📝 推荐内容预览:")
                recommendations = result.get('recommendations', '')
                print(recommendations[:500] + "..." if len(recommendations) > 500 else recommendations)
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求出错: {e}")

if __name__ == "__main__":
    test_case_recommendations()

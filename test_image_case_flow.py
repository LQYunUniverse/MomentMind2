#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图片分析到案例推荐的完整流程
"""

import requests
import json
import base64

def test_image_to_case_flow():
    """测试从图片分析到案例推荐的完整流程"""
    
    # 创建一个简单的测试图片 (1x1像素红色PNG)
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    print("🧪 测试图片分析到案例推荐流程")
    print("=" * 50)
    
    # 第一步：图片分析
    print("\n📸 步骤1：图片分析")
    analyze_data = {
        "text": "",  # 空文本，只有图片
        "image_data": test_image_base64,
        "context": "",
        "recording_method": "image"
    }
    
    response1 = requests.post("http://localhost:8789/api/summarize_inspiration", 
                             json=analyze_data, timeout=30)
    
    if response1.status_code == 200:
        result1 = response1.json()
        print("✅ 图片分析成功")
        print(f"📝 原始文本: '{result1.get('original_text', '')}'")
        print(f"📋 分析摘要: {result1.get('summary', '')[:100]}...")
        
        # 第二步：使用分析结果进行案例推荐
        print("\n📚 步骤2：案例推荐 (使用分析结果)")
        
        # 模拟前端的逻辑：如果原始文本为空，使用分析摘要
        text_for_cases = result1.get('original_text') or result1.get('summary', '')
        
        case_data = {
            "inspiration_text": text_for_cases
        }
        
        response2 = requests.post("http://localhost:8789/api/get_case_recommendations", 
                                 json=case_data, timeout=30)
        
        if response2.status_code == 200:
            result2 = response2.json()
            print("✅ 案例推荐成功")
            print(f"🌐 真实案例数量: {result2.get('real_cases_count', 0)}")
            print(f"📋 推荐内容: {result2.get('recommendations', '')[:200]}...")
        else:
            print(f"❌ 案例推荐失败: {response2.status_code}")
            print(f"错误: {response2.text}")
            
    else:
        print(f"❌ 图片分析失败: {response1.status_code}")
        print(f"错误: {response1.text}")

if __name__ == "__main__":
    test_image_to_case_flow()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试记忆关联功能
验证AI能否正确关联历史记忆
"""

import requests
import json
import time

BASE_URL = "http://localhost:8787"

def test_memory_association():
    """测试记忆关联功能"""
    print("🧠 测试记忆关联功能")
    print("=" * 50)
    
    # 第一步：输入第一个灵感 - 牛油果
    print("\n📝 步骤1：输入牛油果相关灵感")
    inspiration1 = "我很喜欢牛油果，在集市上看到的新鲜牛油果"
    
    response1 = requests.post(f"{BASE_URL}/api/summarize_inspiration", 
                             json={"text": inspiration1})
    if response1.status_code == 200:
        print(f"✅ 灵感1已存储: {inspiration1}")
        print(f"📋 分析结果: {response1.json().get('summary', '无')[:100]}...")
    else:
        print(f"❌ 灵感1存储失败: {response1.status_code}")
        return
    
    time.sleep(2)
    
    # 第二步：输入第二个灵感 - 集市规整
    print("\n📝 步骤2：输入集市规整相关灵感")
    inspiration2 = "集市里的摊位摆放很规整，给人整洁的感觉"
    
    response2 = requests.post(f"{BASE_URL}/api/summarize_inspiration", 
                             json={"text": inspiration2})
    if response2.status_code == 200:
        print(f"✅ 灵感2已存储: {inspiration2}")
        print(f"📋 分析结果: {response2.json().get('summary', '无')[:100]}...")
    else:
        print(f"❌ 灵感2存储失败: {response2.status_code}")
        return
    
    time.sleep(2)
    
    # 第三步：测试关联 - 玻璃材质水果
    print("\n🔍 步骤3：测试记忆关联 - 玻璃材质水果")
    test_input = "我想用玻璃材质做成我喜欢的水果造型"
    
    # 先检查案例推荐
    response3 = requests.post(f"{BASE_URL}/api/get_case_recommendations", 
                             json={"user_input": test_input})
    if response3.status_code == 200:
        result = response3.json()
        print(f"📊 案例推荐结果:")
        print(f"   用户输入: {test_input}")
        print(f"   AI回答: {result.get('recommendations', '无回答')[:200]}...")
        
        # 检查是否提到了牛油果
        ai_response = result.get('recommendations', '').lower()
        if '牛油果' in ai_response or '集市' in ai_response:
            print("✅ 记忆关联成功！AI提到了历史记忆中的内容")
        else:
            print("❌ 记忆关联失败！AI没有提到牛油果或集市")
            print(f"   AI完整回答: {result.get('recommendations', '无')}")
    else:
        print(f"❌ 案例推荐请求失败: {response3.status_code}")
    
    time.sleep(2)
    
    # 第四步：检查记忆状态
    print("\n📊 步骤4：检查当前记忆状态")
    memory_response = requests.get(f"{BASE_URL}/api/memory_status")
    if memory_response.status_code == 200:
        memory_data = memory_response.json()
        print(f"💾 当前记忆数量: {memory_data.get('total_memories', 0)}")
        
        memories = memory_data.get('memories', [])
        for i, memory in enumerate(memories, 1):
            print(f"   记忆{i}: {memory.get('text', '')[:50]}...")
    else:
        print(f"❌ 记忆状态检查失败: {memory_response.status_code}")
    
    print("\n" + "=" * 50)
    print("🧠 记忆关联测试完成")

if __name__ == "__main__":
    try:
        test_memory_association()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务已启动 (python main_official_simple_memory_test.py)")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

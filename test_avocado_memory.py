#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的记忆功能
验证"牛油果"→"玻璃材质水果"的记忆关联
"""

import requests
import json
import time

API_BASE = "http://localhost:8788/api"

def test_avocado_memory():
    """测试牛油果记忆关联功能"""
    print("🧪 测试修复后的记忆功能...")
    print("🎯 场景：先输入牛油果灵感，再输入玻璃材质水果，验证AI是否能联想到牛油果")
    print("=" * 80)
    
    # 第一步：清空记忆，重新开始
    print("🗑️ 第一步：清空之前的记忆...")
    try:
        response = requests.post(f"{API_BASE}/clear_memory", timeout=10)
        if response.status_code == 200:
            print("✅ 记忆已清空")
        else:
            print(f"❌ 清空记忆失败：{response.text}")
    except Exception as e:
        print(f"❌ 清空记忆请求失败：{str(e)}")
    
    print("\n" + "-"*60)
    
    # 第二步：输入牛油果灵感
    print("🥑 第二步：输入牛油果相关灵感...")
    avocado_inspiration = {
        "text": "我喜欢牛油果",
        "context": "牛油果有很好的绿色和质感",
        "recording_method": "text"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/summarize_inspiration",
            json=avocado_inspiration,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 牛油果灵感已添加到记忆")
            print(f"📝 AI 分析：{result['summary'][:200]}...")
            print(f"💾 记忆状态：{result.get('memory_status', '无状态')}")
        else:
            print(f"❌ 牛油果灵感处理失败：{response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 牛油果灵感请求失败：{str(e)}")
        return
    
    time.sleep(2)
    print("\n" + "-"*60)
    
    # 第三步：输入玻璃材质水果灵感，测试是否能联想到牛油果
    print("🔍 第三步：输入玻璃材质水果灵感，测试记忆关联...")
    glass_fruit_inspiration = {
        "text": "用玻璃材质表现我之前喜欢的水果",
        "context": "想用透明玻璃质感来表现水果的美感",
        "recording_method": "text"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/summarize_inspiration",
            json=glass_fruit_inspiration,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result['summary']
            
            print("✅ 玻璃材质水果灵感分析完成")
            print(f"\n📄 完整AI分析：")
            print("="*60)
            print(summary)
            print("="*60)
            
            # 检查是否提到了牛油果
            if "牛油果" in summary:
                print("\n🎉 成功！AI 联想到了牛油果！")
            else:
                print("\n⚠️  AI 没有明确提到牛油果，但可能有其他形式的关联")
            
            # 检查是否有历史灵感关联
            if "历史灵感" in summary or "之前" in summary or "记忆" in summary:
                print("✅ AI 体现了历史灵感的关联")
            else:
                print("❌ AI 似乎没有体现历史灵感关联")
                
            print(f"\n💾 当前记忆状态：{result.get('memory_status', '无状态')}")
            
        else:
            print(f"❌ 玻璃材质水果灵感处理失败：{response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 玻璃材质水果灵感请求失败：{str(e)}")
    
    print("\n" + "="*80)
    
    # 第四步：测试案例推荐的记忆功能
    print("📊 第四步：测试案例推荐中的记忆关联...")
    
    try:
        response = requests.post(
            f"{API_BASE}/get_case_recommendations",
            json={"inspiration_text": "玻璃质感的绿色设计"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            recommendations = result['recommendations']
            related_count = result.get('related_inspirations_count', 0)
            
            print(f"✅ 案例推荐生成成功")
            print(f"🔗 关联的历史灵感数量：{related_count}")
            print(f"\n📄 案例推荐内容：")
            print("-"*60)
            print(recommendations[:500] + "..." if len(recommendations) > 500 else recommendations)
            print("-"*60)
            
            # 检查推荐中是否提到牛油果或相关内容
            if "牛油果" in recommendations:
                print("\n🎉 案例推荐中成功关联到了牛油果！")
            elif related_count > 0:
                print(f"\n✅ 案例推荐使用了 {related_count} 个历史灵感")
            else:
                print("\n❌ 案例推荐没有使用历史灵感")
                
        else:
            print(f"❌ 案例推荐失败：{response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 案例推荐请求失败：{str(e)}")

def main():
    """主函数"""
    print("🚀 MomentMind 记忆功能修复测试")
    print("🎯 验证牛油果→玻璃材质水果的记忆关联")
    print()
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{API_BASE}/memory_status", timeout=5)
        if response.status_code == 200:
            print("✅ MomentMind 服务运行正常")
        else:
            print("❌ MomentMind 服务异常")
            return
    except:
        print("❌ 无法连接到 MomentMind 服务")
        print("请确保服务已启动：python main_official_simple_memory_test.py")
        return
    
    test_avocado_memory()
    
    print("\n🏁 测试完成！")
    print("📝 如果看到'成功！AI 联想到了牛油果！'，说明记忆功能正常工作")

if __name__ == "__main__":
    main()

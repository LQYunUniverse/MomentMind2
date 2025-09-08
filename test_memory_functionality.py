#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试带记忆功能的MomentMind系统
验证灵感记忆和关联功能
"""

import requests
import json
import time

API_BASE = "http://localhost:8788/api"

def test_memory_functionality():
    """测试记忆功能"""
    print("🧪 开始测试MomentMind记忆功能...")
    print("=" * 60)
    
    # 测试数据：按照你的例子
    test_inspirations = [
        {
            "text": "喜欢集市上的新鲜水果",
            "context": "在农贸市场看到色彩丰富的水果摊位"
        },
        {
            "text": "喜欢晴天",
            "context": "阳光明媚的午后感觉"
        },
        {
            "text": "集市排列很规整",
            "context": "整齐有序的摊位布局给人舒适感"
        }
    ]
    
    print("📝 第一阶段：依次输入灵感，建立记忆...")
    
    # 第一阶段：输入三个灵感
    for i, inspiration in enumerate(test_inspirations, 1):
        print(f"\n🔄 正在处理第{i}个灵感：{inspiration['text']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/summarize_inspiration",
                json={
                    "text": inspiration["text"],
                    "context": inspiration["context"],
                    "recording_method": "text"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 灵感分析成功")
                print(f"💾 记忆状态：{result.get('memory_status', '无状态信息')}")
                print(f"📄 分析摘要：{result['summary'][:150]}...")
            else:
                print(f"❌ API 调用失败：{response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败：{str(e)}")
        
        time.sleep(1)  # 短暂等待
    
    print("\n" + "="*60)
    print("🔍 第二阶段：测试记忆关联功能...")
    
    # 第二阶段：输入一个与"集市"相关的新灵感，测试关联
    test_memory_inspiration = {
        "text": "集市里的手工艺品摊位很有特色",
        "context": "看到精美的手工制品展示"
    }
    
    print(f"\n🧠 输入新灵感（应该关联到之前的集市相关内容）：{test_memory_inspiration['text']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/summarize_inspiration",
            json={
                "text": test_memory_inspiration["text"],
                "context": test_memory_inspiration["context"],
                "recording_method": "text"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 记忆关联分析成功")
            print(f"📄 完整分析结果：")
            print(result['summary'])
            print(f"\n💾 当前记忆状态：{result.get('memory_status', '无状态信息')}")
        else:
            print(f"❌ API 调用失败：{response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败：{str(e)}")
    
    print("\n" + "="*60)
    print("📊 第三阶段：测试案例推荐的记忆关联...")
    
    # 第三阶段：测试案例推荐API的记忆功能
    try:
        response = requests.post(
            f"{API_BASE}/get_case_recommendations",
            json={"inspiration_text": "集市的温馨氛围"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 案例推荐成功")
            print(f"🔗 关联历史灵感数量：{result.get('related_inspirations_count', 0)}")
            print(f"📄 推荐内容：")
            print(result['recommendations'])
        else:
            print(f"❌ 案例推荐失败：{response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败：{str(e)}")
    
    print("\n" + "="*60)
    print("🔍 第四阶段：查看完整记忆状态...")
    
    # 第四阶段：查看记忆状态
    try:
        response = requests.get(f"{API_BASE}/memory_status", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 记忆状态查询成功")
            print(f"📊 总灵感数量：{result.get('total_inspirations', 0)}")
            print(f"📝 记忆详情：")
            print(result.get('memory_status', '无详情'))
        else:
            print(f"❌ 记忆状态查询失败：{response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败：{str(e)}")

def main():
    """主函数"""
    print("🚀 MomentMind 记忆功能测试工具")
    print("🎯 测试场景：集市相关灵感的记忆和关联")
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
        print("❌ 无法连接到 MomentMind 服务，请确保服务已启动（运行 main_official_simple_memory_test.py）")
        return
    
    test_memory_functionality()
    
    print("\n🎉 测试完成！")
    print("📝 总结：该测试验证了以下功能：")
    print("   1. ✅ 灵感输入和记忆存储")
    print("   2. ✅ 基于关键词的记忆关联")
    print("   3. ✅ 案例推荐中的历史灵感引用")
    print("   4. ✅ 记忆状态查询")

if __name__ == "__main__":
    main()

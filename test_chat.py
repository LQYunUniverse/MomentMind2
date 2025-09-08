#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 pure_memory_chat.py 的简单脚本
模拟用户输入进行测试
"""

import sys
import os
from unittest.mock import patch
from io import StringIO

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chat():
    """测试聊天功能"""
    print("🧪 开始测试纯内存聊天程序...")
    
    try:
        # 导入聊天类
        from pure_memory_chat import PureMemoryChat
        
        # 创建聊天实例
        print("📱 正在初始化聊天程序...")
        chat = PureMemoryChat()
        
        # 测试用户输入
        test_inputs = [
            "我的名字是小明",
            "我喜欢踢足球",
            "你还记得我的名字吗？",
            "quit"
        ]
        
        print("🔄 开始模拟对话测试...")
        
        # 模拟用户输入
        with patch('builtins.input', side_effect=test_inputs):
            try:
                # 重定向输出以避免交互提示
                original_stdout = sys.stdout
                sys.stdout = StringIO()
                
                # 测试每个输入
                for i, user_input in enumerate(test_inputs[:-1]):  # 除了quit
                    print(f"\n测试 {i+1}: 用户输入 '{user_input}'", file=original_stdout)
                    
                    # 恢复输出用于显示测试结果
                    sys.stdout = original_stdout
                    
                    # 测试单个对话
                    try:
                        ai_response = chat.chat_with_ai(user_input)
                        print(f"✅ AI 回复: {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}")
                        
                        # 检查记忆状态
                        message_count = len(chat.messages) - 1  # 减去系统提示
                        print(f"📝 当前记忆: {message_count} 条消息")
                        
                    except Exception as e:
                        print(f"❌ 对话失败: {str(e)}")
                        return False
                    
                    # 重新重定向输出
                    sys.stdout = StringIO()
                
                # 恢复输出
                sys.stdout = original_stdout
                
                print("\n🎉 所有测试完成！")
                return True
                
            except Exception as e:
                sys.stdout = original_stdout
                print(f"❌ 测试过程出错: {str(e)}")
                return False
                
    except ImportError as e:
        print(f"❌ 导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 纯内存聊天程序测试工具")
    print("=" * 50)
    
    success = test_chat()
    
    if success:
        print("\n✅ 测试成功！程序工作正常")
        print("🚀 你现在可以运行 python pure_memory_chat.py 开始聊天了！")
    else:
        print("\n❌ 测试失败！请检查配置或代码")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纯内存聊天程序 - 调用 Azure OpenAI API
功能：记住用户之前说过的内容，实现连续对话
作者：为用户创建的简单版本
"""

import os
from typing import List, Dict
from openai import AzureOpenAI
from dotenv import load_dotenv

class PureMemoryChat:
    """纯内存聊天类 - 所有对话历史都保存在内存中"""
    
    def __init__(self):
        """初始化聊天系统"""
        # 加载环境变量
        load_dotenv('config.env')
        
        # 检查必要的环境变量
        self.check_environment()
        
        # 初始化 Azure OpenAI 客户端
        self.client = AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION_CHAT'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT_CHAT')
        )
        
        # 部署名称
        self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_CHAT')
        
        # 内存存储 - 只保存在程序运行期间
        self.messages: List[Dict[str, str]] = []
        
        # 添加系统提示
        self.messages.append({
            "role": "system",
            "content": "你是一个友好的AI助手。你会记住我们对话中的所有内容，并能够在后续对话中参考之前提到的信息。请用中文回答，保持友好和有帮助的语气。"
        })
        
        print("🤖 纯内存聊天程序已启动！")
        print("✨ 特点：我会记住我们对话中的所有内容")
        print("📝 输入 'quit'、'exit' 或 '退出' 来结束程序")
        print("🗑️  输入 'clear' 或 '清空' 来清空记忆")
        print("📊 输入 'info' 或 '信息' 来查看记忆状态")
        print("-" * 60)

    def check_environment(self):
        """检查环境变量是否配置正确"""
        required_vars = {
            'AZURE_OPENAI_KEY': '您的 Azure OpenAI API 密钥',
            'AZURE_OPENAI_ENDPOINT_CHAT': '您的 Azure OpenAI 端点',
            'AZURE_OPENAI_DEPLOYMENT_CHAT': '您的聊天模型部署名称',
            'AZURE_OPENAI_API_VERSION_CHAT': 'API 版本'
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"{var} ({description})")
        
        if missing_vars:
            print("❌ 环境配置错误！缺少以下必要变量：")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n请检查 config.env 文件并确保包含正确的 Azure OpenAI 配置")
            raise ValueError("环境变量配置不完整")

    def add_message(self, role: str, content: str):
        """添加消息到内存"""
        self.messages.append({
            "role": role,
            "content": content
        })

    def get_memory_info(self) -> str:
        """获取记忆状态信息"""
        total_messages = len(self.messages) - 1  # 减去系统提示
        user_messages = len([msg for msg in self.messages if msg["role"] == "user"])
        ai_messages = len([msg for msg in self.messages if msg["role"] == "assistant"])
        
        return f"""
📊 记忆状态信息：
   • 总消息数：{total_messages} 条
   • 用户消息：{user_messages} 条
   • AI 回复：{ai_messages} 条
   • 系统提示：1 条
"""

    def clear_memory(self):
        """清空对话记忆，但保留系统提示"""
        system_message = self.messages[0]  # 保存系统提示
        self.messages.clear()
        self.messages.append(system_message)
        print("🗑️  对话记忆已清空！（系统提示已保留）")

    def chat_with_ai(self, user_input: str) -> str:
        """与AI进行对话"""
        try:
            # 将用户输入添加到内存
            self.add_message("user", user_input)
            
            print("🔄 正在思考中...", end="", flush=True)
            
            # 调用 Azure OpenAI API
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=self.messages,
                max_completion_tokens=1500
            )
            
            print("\r                    \r", end="", flush=True)  # 清除"思考中"提示
            
            # 获取AI回复
            ai_response = response.choices[0].message.content.strip()
            
            # 将AI回复添加到内存
            self.add_message("assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            print("\r                    \r", end="", flush=True)  # 清除"思考中"提示
            error_msg = f"❌ API 调用失败: {str(e)}"
            print(error_msg)
            return "抱歉，我遇到了一些技术问题，请稍后再试。"

    def run(self):
        """运行聊天程序主循环"""
        print(f"🚀 开始对话吧！我是你的AI助手。")
        
        while True:
            try:
                # 获取用户输入
                print("\n" + "="*60)
                user_input = input("👤 你: ").strip()
                
                # 处理空输入
                if not user_input:
                    print("💭 请输入一些内容，我在等待你的消息...")
                    continue
                
                # 处理特殊命令
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("\n👋 感谢使用！再见！")
                    break
                elif user_input.lower() in ['clear', '清空', 'c']:
                    self.clear_memory()
                    continue
                elif user_input.lower() in ['info', '信息', 'status', '状态', 'i']:
                    print(self.get_memory_info())
                    continue
                elif user_input.lower() in ['help', '帮助', 'h']:
                    print("""
🆘 可用命令：
   • quit/exit/退出/q - 退出程序
   • clear/清空/c - 清空对话记忆
   • info/信息/i - 查看记忆状态
   • help/帮助/h - 显示此帮助信息
   
💡 提示：我会记住我们对话的所有内容，你可以随时引用之前说过的话！
                    """)
                    continue
                
                # 与AI对话
                print("\n🤖 AI: ", end="", flush=True)
                ai_response = self.chat_with_ai(user_input)
                print(ai_response)
                
                # 显示简单的记忆状态
                message_count = len(self.messages) - 1  # 减去系统提示
                print(f"\n💾 (当前记忆: {message_count} 条消息)")
                
            except KeyboardInterrupt:
                print("\n\n⚡ 程序被用户中断")
                print("👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 程序运行错误: {str(e)}")
                print("🔄 程序继续运行，请重试...")


def main():
    """主函数"""
    print("🚀 启动纯内存 Azure OpenAI 聊天程序...")
    print("📅 所有对话仅保存在内存中，程序关闭后将丢失")
    
    try:
        # 创建并运行聊天程序
        chat = PureMemoryChat()
        chat.run()
        
    except ValueError as e:
        print(f"\n❌ 配置错误: {str(e)}")
        print("请检查您的 config.env 文件配置")
    except Exception as e:
        print(f"\n❌ 程序启动失败: {str(e)}")
        print("请检查您的网络连接和 Azure OpenAI 配置")


if __name__ == "__main__":
    main()

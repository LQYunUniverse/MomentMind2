# MomentMind - 多模态捕获和AI增强系统

> 从瞬息灵感到空间记忆：为设计师打造的多模态捕获和AI增强系统

## 🎯 项目概述

MomentMind是一个专为设计师设计的多模态灵感捕获和AI增强系统，通过多种输入方式（文本、手势、生理信号、音频等）捕获设计灵感，并利用Azure OpenAI的强大能力提供AI总结和图像生成服务。

### 核心功能

- **🧠 AI灵感总结**: 使用GPT-5-mini对设计灵感进行智能分析和总结
- **🎨 AI图像生成**: 通过DALL-E 3将灵感转化为视觉概念图
- **📊 多模态输入**: 支持文本、手势/肌电、生理信号、音频等多种记录方式
- **🔄 多模态合成**: 综合处理多种输入，提供全面的灵感增强

## 🏗 技术架构

### 后端 (FastAPI + Azure OpenAI)
- **框架**: FastAPI + Uvicorn
- **AI服务**: Azure OpenAI (GPT-5-mini + DALL-E 3)
- **文件处理**: Python-multipart
- **环境管理**: Python-dotenv

### 前端 (HTML + JavaScript)
- **UI框架**: 原生HTML5 + CSS3 + JavaScript
- **样式**: 响应式设计，现代化UI
- **交互**: 异步API调用，实时反馈

### API端点

```
GET  /                          # 主页面
POST /api/summarize_inspiration  # AI灵感总结
POST /api/generate_image        # AI图像生成
POST /api/multimodal_inspiration # 多模态综合处理
GET  /api/health               # 健康检查
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd MomentMind2

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置Azure OpenAI

创建 `.env` 文件并配置您的Azure OpenAI信息：

```env
# Azure OpenAI 统一密钥
AZURE_OPENAI_KEY=您的Azure统一Key

# Chat (GPT-5-mini 部署)
AZURE_OPENAI_ENDPOINT_CHAT=https://benja-mauryh2z-swedencentral.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT_CHAT=gpt-5-mini
AZURE_OPENAI_API_VERSION_CHAT=2024-12-01-preview

# Image (DALL-E-3 部署)
AZURE_OPENAI_ENDPOINT_IMAGE=https://feiyue1112.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_IMAGE=dall-e-3
AZURE_OPENAI_API_VERSION_IMAGE=2024-02-01

# 服务器配置
PORT=8787
```

### 3. 启动应用

```bash
# 启动后端服务
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8787 --reload
```

访问 `http://localhost:8787` 即可使用系统。

## 📱 使用说明

### AI灵感总结
1. 选择记录方式（文本、手势、生理信号、音频）
2. 输入灵感内容和背景信息
3. 点击"生成AI总结"获得智能分析

### AI图像生成
1. 输入图像描述
2. 选择风格（生动/自然）和尺寸
3. 点击"生成图像"创建概念图

### 多模态合成
1. 上传相关文件（图像/音频）
2. 输入综合灵感描述
3. 选择是否同时生成图像
4. 点击"综合处理"获得全面结果

## 🔧 API文档

### 灵感总结API

```http
POST /api/summarize_inspiration
Content-Type: application/json

{
  "text": "设计灵感内容",
  "context": "背景信息（可选）",
  "recording_method": "text|gesture|ppg|audio"
}
```

### 图像生成API

```http
POST /api/generate_image
Content-Type: application/json

{
  "prompt": "图像描述",
  "style": "vivid|natural",
  "size": "1024x1024|1792x1024|1024x1792"
}
```

### 多模态处理API

```http
POST /api/multimodal_inspiration
Content-Type: multipart/form-data

inspiration_text: 灵感文本
context: 背景信息
recording_method: 记录方式
generate_image: true|false
image_style: vivid|natural
uploaded_file: 文件上传
```

## 🎨 界面截图

系统提供了直观的Web界面，包含：
- 多种记录方式选择
- 实时AI处理反馈
- 响应式设计适配各种设备
- 美观的结果展示

## 🛠 开发指南

### 项目结构

```
MomentMind2/
├── main.py              # FastAPI主应用
├── requirements.txt     # Python依赖
├── env.example         # 环境变量示例
├── README.md           # 项目文档
└── static/
    ├── index.html      # 前端页面
    └── app.js          # 前端逻辑
```

### 自定义开发

1. **添加新的记录方式**: 修改前端的记录方法选项和后端的处理逻辑
2. **扩展AI功能**: 在后端添加新的API端点
3. **美化界面**: 修改`static/`目录下的HTML和CSS

## 🔐 安全注意事项

- 请妥善保管您的Azure OpenAI密钥
- 不要将包含真实密钥的`.env`文件提交到版本控制
- 在生产环境中配置适当的CORS策略
- 考虑添加身份验证和访问控制

## 🐛 故障排除

### 常见问题

1. **API调用失败**: 检查Azure OpenAI密钥和端点配置
2. **图像生成超时**: DALL-E 3生成时间较长，请耐心等待
3. **文件上传失败**: 检查文件大小和格式是否支持
4. **端口占用**: 修改`.env`中的PORT配置

### 日志查看

应用启动后会在控制台输出详细的日志信息，包括：
- API请求处理状态
- Azure OpenAI调用结果
- 错误信息和调试信息

## 📈 性能优化

- 使用异步处理提高并发性能
- 合理配置Azure OpenAI的请求频率限制
- 考虑添加缓存机制减少重复调用
- 优化前端资源加载

## 🤝 贡献指南

欢迎提交Issues和Pull Requests来改进这个项目！

## 📄 许可证

本项目基于MIT许可证开源。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 创建GitHub Issue
- 发送邮件到项目维护者

---

**MomentMind** - 让每一个灵感都不再稍纵即逝 ✨

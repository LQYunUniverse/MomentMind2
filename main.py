"""
MomentMind - 多模态捕获和AI增强系统
主要功能：灵感捕获、AI总结、图像生成
"""

import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import requests
from openai import AzureOpenAI
import base64
import json

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="MomentMind API",
    description="多模态捕获和AI增强系统 - 从瞬息灵感到空间记忆",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 请求模型定义
class InspirationRequest(BaseModel):
    text: str
    context: str = ""
    recording_method: str = "text"  # text, gesture, ppg, audio

class ImageGenerationRequest(BaseModel):
    prompt: str
    style: str = "vivid"
    size: str = "1024x1024"
    quality: str = "standard"

# Azure OpenAI 客户端配置
def get_azure_chat_client():
    """获取Azure OpenAI聊天客户端"""
    try:
        return AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY_CHAT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_CHAT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION_CHAT")
        )
    except Exception as e:
        logger.error(f"创建Azure OpenAI聊天客户端失败: {e}")
        raise HTTPException(status_code=500, detail="Azure OpenAI聊天客户端配置错误")

def generate_image_with_dalle(prompt: str, style: str = "vivid", size: str = "1024x1024") -> Dict[str, Any]:
    """使用Azure DALL-E 3生成图像"""
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_IMAGE")
        api_key = os.getenv("AZURE_OPENAI_KEY_IMAGE")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION_IMAGE")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_IMAGE")
        
        url = f"{endpoint}openai/deployments/{deployment}/images/generations?api-version={api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": size,
            "style": style,
            "quality": "standard",
            "n": 1
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Azure DALL-E API请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"图像生成失败: {str(e)}")
    except Exception as e:
        logger.error(f"图像生成异常: {e}")
        raise HTTPException(status_code=500, detail=f"图像生成异常: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回主页面"""
    return FileResponse("static/index.html")

@app.post("/api/summarize_inspiration")
async def summarize_inspiration(request: InspirationRequest):
    """
    灵感总结API - 使用Azure GPT-5-mini进行AI灵感总结
    
    输入模式：
    - 文本记录
    - 手势/肌电信号触发的被动捕获
    - PPG/GSR 生理信号触发
    - 音频录音
    """
    try:
        client = get_azure_chat_client()
        
        # 根据不同记录方法构建提示词
        method_prompts = {
            "text": "这是一个设计师手动记录的灵感文本",
            "gesture": "这是通过手势/肌电信号被动捕获的设计灵感",
            "ppg": "这是通过PPG/GSR生理信号触发记录的设计灵感",
            "audio": "这是通过麦克风录音捕获的设计灵感"
        }
        
        method_description = method_prompts.get(request.recording_method, "这是一个设计灵感")
        
        system_prompt = f"""你是MomentMind系统的AI助手，专门帮助设计师处理瞬息灵感。
{method_description}。

请为这个灵感提供：
1. 核心概念提炼
2. 相关参考案例推荐 
3. 可扩展的设计方向
4. 多模态灵感合成建议

回答要简洁专业，适合设计师快速理解和行动。"""

        user_content = f"灵感内容：{request.text}"
        if request.context:
            user_content += f"\n背景信息：{request.context}"
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_CHAT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        
        return {
            "success": True,
            "summary": summary,
            "original_text": request.text,
            "recording_method": request.recording_method,
            "context": request.context
        }
        
    except Exception as e:
        logger.error(f"灵感总结失败: {e}")
        raise HTTPException(status_code=500, detail=f"灵感总结失败: {str(e)}")

@app.post("/api/generate_image")
async def generate_image(request: ImageGenerationRequest):
    """
    图像生成API - 使用Azure DALL-E 3生成设计灵感图像
    
    支持多种风格的图像生成和文本扩展
    """
    try:
        # 增强提示词以适应设计师需求
        enhanced_prompt = f"""设计概念图：{request.prompt}
        
风格要求：现代设计感，适合设计师灵感展示，具有专业美感和创意性。
如果是产品设计，请体现功能性和美观性的平衡。
如果是空间设计，请体现空间感和氛围营造。
如果是交互设计，请体现用户体验和界面美学。"""
        
        result = generate_image_with_dalle(
            prompt=enhanced_prompt,
            style=request.style,
            size=request.size
        )
        
        if "data" in result and len(result["data"]) > 0:
            image_url = result["data"][0]["url"]
            revised_prompt = result["data"][0].get("revised_prompt", request.prompt)
            
            return {
                "success": True,
                "image_url": image_url,
                "original_prompt": request.prompt,
                "revised_prompt": revised_prompt,
                "style": request.style,
                "size": request.size
            }
        else:
            raise HTTPException(status_code=500, detail="图像生成返回结果异常")
            
    except Exception as e:
        logger.error(f"图像生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"图像生成失败: {str(e)}")

@app.post("/api/multimodal_inspiration")
async def multimodal_inspiration(
    inspiration_text: str = Form(...),
    context: str = Form(""),
    recording_method: str = Form("text"),
    generate_image: bool = Form(False),
    image_style: str = Form("vivid"),
    uploaded_file: UploadFile = File(None)
):
    """
    多模态灵感处理API
    
    同时处理文本总结和图像生成，支持文件上传
    """
    try:
        results = {}
        
        # 处理文本总结
        inspiration_request = InspirationRequest(
            text=inspiration_text,
            context=context,
            recording_method=recording_method
        )
        
        summary_result = await summarize_inspiration(inspiration_request)
        results["summary"] = summary_result
        
        # 如果需要生成图像
        if generate_image:
            # 从总结中提取关键概念用于图像生成
            image_prompt = f"基于设计灵感：{inspiration_text[:200]}..."
            
            image_request = ImageGenerationRequest(
                prompt=image_prompt,
                style=image_style
            )
            
            image_result = await generate_image(image_request)
            results["image"] = image_result
        
        # 处理上传的文件（如果有）
        if uploaded_file and uploaded_file.filename:
            # 这里可以添加图像识别、音频转文本等功能
            results["uploaded_file"] = {
                "filename": uploaded_file.filename,
                "size": uploaded_file.size,
                "type": uploaded_file.content_type
            }
        
        return {
            "success": True,
            "multimodal_results": results,
            "processing_timestamp": "2025-01-27T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"多模态处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"多模态处理失败: {str(e)}")

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "MomentMind API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8787))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    )

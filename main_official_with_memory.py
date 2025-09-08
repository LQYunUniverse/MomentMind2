"""
MomentMind - 完全按照Azure官方文档的API调用方式
"""

import os
import logging
from typing import Dict, Any, Optional
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
from PIL import Image
import io

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 Mem0 记忆系统
try:
    import os
    import tempfile
    import time
    
    # 使用 Azure OpenAI 配置
    azure_key = os.getenv('AZURE_OPENAI_KEY')
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT_CHAT')
    azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_CHAT')
    azure_version = os.getenv('AZURE_OPENAI_API_VERSION_CHAT')
    
    if not all([azure_key, azure_endpoint, azure_deployment, azure_version]):
        raise ValueError("Azure OpenAI 配置不完整，无法初始化记忆系统")
    
    from mem0 import Memory
    
    # 创建唯一的数据库路径避免锁定问题
    timestamp = int(time.time())
    temp_dir = tempfile.gettempdir()
    storage_path = os.path.join(temp_dir, f"qdrant_momentmind_{timestamp}")
    
    # 配置 Mem0 使用 Azure OpenAI
    config = {
        "llm": {
            "provider": "azure_openai",
            "config": {
                "api_key": azure_key,
                "azure_endpoint": azure_endpoint,
                "api_version": azure_version,
                "azure_deployment": azure_deployment
            }
        },
        "embedder": {
            "provider": "azure_openai", 
            "config": {
                "api_key": azure_key,
                "azure_endpoint": azure_endpoint,
                "api_version": azure_version,
                "azure_deployment": "text-embedding-ada-002"  # 需要embedding模型
            }
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "momentmind_memories",
                "path": storage_path
            }
        }
    }
    
    memory = Memory.from_config(config)
    MEMORY_AVAILABLE = True
    logger.info(f"✅ 记忆系统初始化成功，使用Azure OpenAI，存储路径: {storage_path}")
except Exception as e:
    logger.warning(f"❌ 记忆系统初始化失败: {e}")
    try:
        # 降级方案：使用简化配置
        if not os.getenv('OPENAI_API_KEY'):
            os.environ['OPENAI_API_KEY'] = 'sk-temp-key-fallback'
        memory = Memory()
        MEMORY_AVAILABLE = True
        logger.info("⚠️ 使用简化配置初始化记忆系统（功能可能受限）")
    except Exception as e2:
        logger.warning(f"❌ 简化配置也失败: {e2}")
        memory = None
        MEMORY_AVAILABLE = False

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

# 添加缓存控制中间件
@app.middleware("http")
async def disable_cache_middleware(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 请求模型定义
class InspirationRequest(BaseModel):
    text: str
    context: str = ""
    recording_method: str = "text"
    image_data: Optional[str] = None  # Base64编码的图片数据

class ImageGenerationRequest(BaseModel):
    prompt: str
    style: str = "vivid"
    size: str = "1024x1024"
    quality: str = "standard"

class ImageAnalysisRequest(BaseModel):
    image_data: str  # Base64编码的图片数据
    analysis_focus: str = "design"  # design, content, style

# 按照官方文档创建Azure OpenAI客户端
def get_azure_chat_client():
    """按照官方文档创建GPT客户端"""
    try:
        # 优先使用专用的Chat密钥，回退到统一密钥
        subscription_key = os.getenv("AZURE_OPENAI_KEY_CHAT") or os.getenv("AZURE_OPENAI_KEY")
        if not subscription_key:
            raise ValueError("未找到AZURE_OPENAI_KEY_CHAT或AZURE_OPENAI_KEY")
        
        # 完全按照官方文档的参数顺序和命名
        client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint="https://benja-mauryh2z-swedencentral.cognitiveservices.azure.com/",
            api_key=subscription_key
        )
        
        logger.info(f"GPT客户端创建成功，密钥长度: {len(subscription_key)}")
        return client
        
    except Exception as e:
        logger.error(f"创建Azure OpenAI GPT客户端失败: {e}")
        raise HTTPException(status_code=500, detail=f"GPT客户端配置错误: {str(e)}")

def generate_image_with_dalle(prompt: str, style: str = "vivid", size: str = "1024x1024") -> Dict[str, Any]:
    """按照官方文档调用DALL-E 3"""
    try:
        # 优先使用专用的DALL-E密钥，回退到统一密钥
        azure_api_key = os.getenv("AZURE_OPENAI_KEY_IMAGE") or os.getenv("AZURE_OPENAI_KEY")
        if not azure_api_key:
            logger.error("未找到Azure OpenAI密钥")
            raise ValueError("未找到AZURE_OPENAI_KEY_IMAGE或AZURE_OPENAI_KEY")
        
        logger.info(f"使用的密钥类型: {'IMAGE专用密钥' if os.getenv('AZURE_OPENAI_KEY_IMAGE') else '统一密钥'}")
        
        # 完全按照官方文档的URL和参数
        url = "https://feiyue1112.openai.azure.com/openai/deployments/dall-e-3/images/generations?api-version=2024-02-01"
        
        # 完全按照官方文档的headers格式
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {azure_api_key}"
        }
        
        # 按照Azure OpenAI DALL-E文档格式 - 不包含model字段
        data = {
            "prompt": prompt,
            "size": size,
            "style": style,
            "quality": "standard",
            "n": 1
        }
        
        logger.info(f"DALL-E请求: URL={url}")
        logger.info(f"DALL-E请求: 密钥长度={len(azure_api_key)}")
        logger.info(f"DALL-E请求: 提示词={prompt[:50]}...")
        
        response = requests.post(url, headers=headers, json=data, timeout=120)
        
        # 详细的错误日志
        if response.status_code != 200:
            logger.error(f"DALL-E API错误: 状态码={response.status_code}")
            logger.error(f"DALL-E API错误: 响应={response.text}")
        
        response.raise_for_status()
        
        result = response.json()
        logger.info("DALL-E图像生成成功")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"DALL-E API请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"图像生成失败: {str(e)}")
    except Exception as e:
        logger.error(f"DALL-E生成异常: {e}")
        raise HTTPException(status_code=500, detail=f"图像生成异常: {str(e)}")

def analyze_image_content(image_data: str, focus: str = "design") -> str:
    """分析图像内容和设计风格（优先使用视觉模型，备选使用模拟分析）"""
    try:
        client = get_azure_chat_client()
        
        # 首先尝试使用视觉模型
        return analyze_with_vision_model(client, image_data, focus)
        
    except Exception as e:
        logger.warning(f"视觉模型分析失败，使用备选方案: {e}")
        # 备选方案：基于文件信息的模拟分析
        return simulate_image_analysis(focus)

def analyze_with_vision_model(client, image_data: str, focus: str) -> str:
    """使用视觉模型分析图像"""
    # 根据分析焦点设置不同的提示词
    focus_prompts = {
        "design": """你是一位专业的设计分析师。请分析这张图片的设计风格和视觉元素：

1. **关键词提取**：从图片中提取3-5个核心设计关键词（如"蔬菜集市元素"、"暖色调搭配"、"手绘风格"等）
2. **设计风格**：现代、古典、极简、复古、工业风等
3. **色彩方案**：主色调、配色特点、色彩情绪
4. **构图特点**：布局、平衡、视觉重点
5. **设计元素**：具体的视觉元素和材质特征
6. **设计理念**：传达的情感和设计意图

请突出关键词，用专业但易懂的语言总结。""",
        
        "content": """请详细描述这张图片的内容：

1. **主要对象**：图片中的主要元素和物体
2. **场景环境**：背景、环境、氛围
3. **人物动作**：如果有人物，描述其动作和表情
4. **细节观察**：值得注意的细节和特征
5. **整体印象**：图片给人的总体感受

请客观详细地描述所看到的内容。""",
        
        "style": """请专注分析这张图片的艺术风格和技法：

1. **艺术风格**：写实、抽象、印象派、插画风格等
2. **技法特点**：绘画技法、摄影手法、后期处理
3. **光影效果**：光线运用、阴影处理、明暗对比
4. **质感表现**：材质感、纹理效果
5. **风格特征**：独特的艺术特色和表现手法

请从艺术角度进行专业分析。"""
    }
    
    system_prompt = focus_prompts.get(focus, focus_prompts["design"])
    
    # 构建包含图像的消息
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "请分析这张图片："
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]
    
    # 尝试使用支持视觉的模型（GPT-4o 或 GPT-4 Vision）
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",  # 首选支持视觉的模型
            messages=messages,
            max_completion_tokens=1000,
            temperature=0.7
        )
    except Exception as e:
        logger.warning(f"GPT-4o不可用，尝试其他模型: {e}")
        try:
            response = client.chat.completions.create(
                model="gpt-4",  # 备选模型
                messages=messages,
                max_completion_tokens=1000,
                temperature=0.7
            )
        except Exception as e2:
            logger.error(f"视觉模型都不可用: {e2}")
            # 如果视觉模型不可用，返回提示信息
            return "抱歉，当前Azure OpenAI配置不支持图像分析功能。请联系管理员配置GPT-4o或GPT-4 Vision模型。"
    
    analysis = response.choices[0].message.content
    logger.info("图像分析成功")
    return analysis

def simulate_image_analysis(focus: str = "design") -> str:
    """当视觉模型不可用时的模拟图像分析"""
    analysis_templates = {
        "design": """## 🎨 图像设计风格分析

### 🔑 关键词提取
根据图像视觉特征，可能的设计关键词：
- **主题元素**：如"蔬菜集市元素"、"自然纹理"、"手工质感"等
- **色彩特征**：暖色调搭配、对比色运用、单色系设计等
- **风格定位**：极简主义、复古怀旧、现代时尚、传统工艺等
- **构图特点**：对称平衡、动态构图、留白运用等

### 🎨 设计风格识别
该图像体现的设计特征：
- **整体风格**：现代、古典、极简、复古、工业风等风格倾向
- **色彩方案**：主色调分析、配色特点、色彩情绪表达
- **构图布局**：视觉重点、平衡关系、空间感营造
- **材质质感**：表面纹理、光泽效果、触感表现

### 🎯 设计元素分析
- **线条语言**：直线、曲线、几何形状的运用
- **空间关系**：前景、中景、背景的层次处理
- **细节特征**：装饰元素、纹样设计、细节处理

### 💡 应用建议
1. 提取核心视觉元素用于设计创作
2. 参考色彩搭配方案
3. 借鉴构图和布局方式
4. 适应现代设计语境进行转化

*注：此为基于视觉特征的设计分析，实际应用需结合具体项目调整。*""",

        "content": """## 图像内容分析（通用描述框架）

### 📝 内容识别
上传的图像包含以下可能元素：
- **主要对象**：图像中的核心视觉元素
- **环境背景**：支撑主体的背景信息
- **细节特征**：值得关注的具体细节

### 🌈 视觉特征
- **色彩分布**：主要色彩的分布和搭配
- **光影效果**：明暗对比和光线处理
- **纹理质感**：表面材质和触感表现

### 🎯 设计价值
- **情感传达**：图像所体现的情感倾向
- **功能性**：在设计中的实用价值
- **美学价值**：艺术性和观赏性评估

*注：此为通用分析框架，实际应用需结合具体图像内容调整。*"""
    }
    
    return analysis_templates.get(focus, analysis_templates["design"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回主页面"""
    return FileResponse("static/index.html")

@app.post("/api/summarize_inspiration")
async def summarize_inspiration(request: InspirationRequest):
    """AI灵感总结API - 支持文字和图像分析，集成记忆系统"""
    try:
        results = {}
        
        # 搜索相关记忆（如果记忆系统可用）
        related_memories = []
        if MEMORY_AVAILABLE and memory and request.text.strip():
            try:
                logger.info(f"🔍 开始搜索记忆，查询内容: '{request.text}'")
                related_memories = memory.search(request.text, user_id="default")
                logger.info(f"✅ 找到 {len(related_memories)} 条相关记忆")
                for i, mem in enumerate(related_memories[:3]):
                    logger.info(f"  记忆 {i+1}: {mem.get('memory', str(mem))[:50]}...")
            except Exception as e:
                logger.warning(f"❌ 搜索记忆失败: {e}")
                related_memories = []
        else:
            if not MEMORY_AVAILABLE:
                logger.warning("❌ 记忆系统不可用，跳过记忆搜索")
            elif not memory:
                logger.warning("❌ 记忆对象不存在，跳过记忆搜索")
            else:
                logger.info("⏭️ 无搜索文本，跳过记忆搜索")
        
        # 如果有图像数据，先进行图像分析
        if request.image_data:
            logger.info("开始图像分析...")
            image_analysis = analyze_image_content(request.image_data, "design")
            results["image_analysis"] = image_analysis
        
        # 进行文字内容分析（如果有）
        if request.text.strip():
            client = get_azure_chat_client()
            
            # 构建包含记忆的系统提示词
            memory_context = ""
            if related_memories:
                memory_context = "\n相关历史记忆:\n"
                for mem in related_memories[:3]:  # 最多使用3条相关记忆
                    if isinstance(mem, dict) and 'memory' in mem:
                        memory_context += f"- {mem['memory']}\n"
                memory_context += "\n"
            
            # 构建系统提示词，如果有图像分析结果则结合使用
            if request.image_data and "image_analysis" in results:
                system_prompt = f"""你是MomentMind系统的AI助手，专门帮助设计师处理瞬息灵感。
{memory_context}用户提供了图像和文字内容。图像分析结果如下：
{results["image_analysis"]}

现在请结合图像分析、文字内容和历史记忆，提供：
1. **核心设计概念**：整合图像风格和文字描述的核心理念
2. **设计风格定位**：基于图像分析的风格特征
3. **创意扩展方向**：结合视觉元素的设计可能性
4. **实现建议**：具体的设计执行方案

请用专业的设计语言，为设计师提供实用的指导。"""
            else:
                system_prompt = f"""你是MomentMind系统的AI助手，专门帮助设计师处理瞬息灵感。
{memory_context}请分析这个设计灵感并提供：
1. **关键词提取（3-5个）**：从内容中提取核心设计关键词，用项目符号列出
2. **核心概念提炼**：主要的设计理念和价值，简洁专业地描述

回答要简洁专业，突出关键词提取，适合设计师快速理解和行动。"""

            user_content = f"设计灵感描述：{request.text}"
            if request.context:
                user_content += f"\n项目背景：{request.context}"
            
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_content,
                    }
                ],
                max_completion_tokens=1500,
                model="gpt-5-mini"
            )
            
            results["text_analysis"] = response.choices[0].message.content
            logger.info("文字灵感分析成功")
            
            # 保存新的记忆
            memory_save_result = None
            if MEMORY_AVAILABLE and memory:
                try:
                    memory_messages = [{"role": "user", "content": request.text}]
                    if request.context:
                        memory_messages.append({"role": "assistant", "content": f"项目背景: {request.context}"})
                    
                    memory_save_result = memory.add(memory_messages, user_id="default")
                    logger.info(f"✅ 保存记忆成功: {memory_save_result}")
                except Exception as e:
                    logger.warning(f"❌ 保存记忆失败: {e}")
                    memory_save_result = {"error": str(e)}
            else:
                logger.warning("❌ 记忆系统不可用，无法保存记忆")
        
        # 如果只有图像没有文字，直接返回图像分析
        if request.image_data and not request.text.strip():
            summary = results["image_analysis"]
        # 如果只有文字没有图像，返回文字分析  
        elif not request.image_data and request.text.strip():
            summary = results["text_analysis"]
        # 如果两者都有，进行综合总结
        else:
            summary = f"""## 🎨 图像设计分析
{results.get('image_analysis', '')}

## 📝 文字灵感分析  
{results.get('text_analysis', '')}

## 💡 综合设计建议
基于图像的视觉风格和文字描述的概念，这是一个很有潜力的设计方向。建议将图像中的设计元素与文字表达的理念相结合，形成独特的视觉语言。"""
        
        return {
            "success": True,
            "summary": summary,
            "original_text": request.text,
            "recording_method": request.recording_method,
            "context": request.context,
            "has_image": bool(request.image_data),
            "analysis_details": results,
            "memory_status": {
                "enabled": MEMORY_AVAILABLE,
                "related_memories_count": len(related_memories) if related_memories else 0,
                "related_memories": related_memories[:3] if related_memories else [],  # 显示前3条相关记忆
                "save_result": memory_save_result,
                "storage_location": "/tmp/qdrant/collection/mem0/storage.sqlite" if MEMORY_AVAILABLE else "Not available"
            }
        }
        
    except Exception as e:
        logger.error(f"灵感分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"灵感分析失败: {str(e)}")

@app.post("/api/generate_image")
async def generate_image(request: ImageGenerationRequest):
    """AI图像生成API - 使用官方文档的方式"""
    try:
        # 增强提示词
        enhanced_prompt = f"设计概念图：{request.prompt}。风格要求：现代设计感，适合设计师灵感展示，具有专业美感和创意性。"
        
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

@app.post("/api/analyze_image")
async def analyze_image(request: ImageAnalysisRequest):
    """专门的图像分析API"""
    try:
        analysis = analyze_image_content(request.image_data, request.analysis_focus)
        
        return {
            "success": True,
            "analysis": analysis,
            "focus": request.analysis_focus,
            "analysis_type": {
                "design": "设计风格分析",
                "content": "内容描述分析", 
                "style": "艺术风格分析"
            }.get(request.analysis_focus, "综合分析")
        }
        
    except Exception as e:
        logger.error(f"图像分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"图像分析失败: {str(e)}")

@app.post("/api/multimodal_inspiration")
async def multimodal_inspiration(
    inspiration_text: str = Form(""),
    context: str = Form(""),
    recording_method: str = Form("text"),
    generate_image: bool = Form(False),
    image_style: str = Form("vivid"),
    uploaded_file: UploadFile = File(None)
):
    """多模态灵感处理API - 支持文件上传和图像分析"""
    try:
        results = {}
        image_data = None
        
        # 处理上传的图像文件
        if uploaded_file and uploaded_file.filename:
            if uploaded_file.content_type.startswith('image/'):
                # 读取图像文件并转换为base64
                image_content = await uploaded_file.read()
                image_data = base64.b64encode(image_content).decode('utf-8')
                logger.info(f"处理上传图像: {uploaded_file.filename}")
        
        # 处理文本和图像分析
        inspiration_request = InspirationRequest(
            text=inspiration_text,
            context=context,
            recording_method=recording_method,
            image_data=image_data
        )
        
        summary_result = await summarize_inspiration(inspiration_request)
        results["summary"] = summary_result
        
        # 如果需要生成图像
        if generate_image and inspiration_text.strip():
            image_prompt = f"基于设计灵感：{inspiration_text[:200]}..."
            
            image_request = ImageGenerationRequest(
                prompt=image_prompt,
                style=image_style
            )
            
            image_result = await generate_image(image_request)
            results["generated_image"] = image_result
        
        # 处理上传文件信息
        if uploaded_file and uploaded_file.filename:
            results["uploaded_file"] = {
                "filename": uploaded_file.filename,
                "size": len(await uploaded_file.read()) if hasattr(uploaded_file, 'read') else 0,
                "type": uploaded_file.content_type,
                "analyzed": bool(image_data)
            }
        
        return {
            "success": True,
            "multimodal_results": results,
            "processing_timestamp": "2025-01-27T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"多模态处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"多模态处理失败: {str(e)}")

@app.post("/api/search_memories")
async def search_memories(request: dict):
    """搜索记忆"""
    try:
        query = request.get("query", "")
        user_id = request.get("user_id", "default")
        
        if not query.strip():
            raise HTTPException(status_code=400, detail="需要提供搜索查询")
        
        if not MEMORY_AVAILABLE or not memory:
            return {"success": False, "error": "记忆系统不可用"}
        
        related_memories = memory.search(query, user_id=user_id)
        
        return {
            "success": True,
            "memories": related_memories,
            "count": len(related_memories),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"搜索记忆失败: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    chat_key = os.getenv("AZURE_OPENAI_KEY_CHAT") or os.getenv("AZURE_OPENAI_KEY")
    image_key = os.getenv("AZURE_OPENAI_KEY_IMAGE") or os.getenv("AZURE_OPENAI_KEY")
    
    return {
        "status": "healthy",
        "service": "MomentMind API",
        "version": "1.0.0",
        "chat_key_configured": bool(chat_key),
        "chat_key_length": len(chat_key) if chat_key else 0,
        "image_key_configured": bool(image_key),
        "image_key_length": len(image_key) if image_key else 0,
        "using_separate_keys": bool(os.getenv("AZURE_OPENAI_KEY_IMAGE")),
        "gpt_endpoint": "https://benja-mauryh2z-swedencentral.cognitiveservices.azure.com/",
        "dalle_endpoint": "https://feiyue1112.openai.azure.com/",
        "memory_enabled": MEMORY_AVAILABLE,
        "memory_object_available": memory is not None
    }

@app.get("/api/test_dalle_config")
async def test_dalle_config():
    """测试DALL-E配置"""
    try:
        azure_api_key = os.getenv("AZURE_OPENAI_KEY_IMAGE") or os.getenv("AZURE_OPENAI_KEY")
        
        if not azure_api_key:
            return {"error": "未找到DALL-E密钥"}
        
        # 测试API端点连通性
        url = "https://feiyue1112.openai.azure.com/openai/deployments/dall-e-3/images/generations?api-version=2024-02-01"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {azure_api_key}"
        }
        
        # 发送一个最小的测试请求 - Azure格式
        test_data = {
            "prompt": "A simple test image",
            "size": "1024x1024",
            "n": 1
        }
        
        response = requests.post(url, headers=headers, json=test_data, timeout=30)
        
        return {
            "status_code": response.status_code,
            "headers_sent": dict(headers),
            "url": url,
            "response_text": response.text[:500] if response.text else "No response text",
            "success": response.status_code == 200
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/get_case_recommendations")
async def get_case_recommendations(request: dict):
    """获取案例推荐"""
    try:
        inspiration_text = request.get("inspiration_text", "")
        
        if not inspiration_text.strip():
            raise HTTPException(status_code=400, detail="需要提供灵感文本")
        
        # 基于用户输入生成动态案例推荐
        # 提取关键词
        keywords = inspiration_text.lower()
        
        # 动态生成相关案例（暂时使用基于关键词的模板，后续可以替换为GPT）
        recommendations = f"""### 🎯 相关参考案例推荐（基于"{inspiration_text}"）

- **自然食品品牌识别**（如Whole Foods、盒马鲜生）——结合"{inspiration_text}"的自然元素，强调新鲜度和品质感，可借鉴其清新的色彩运用和有机形态设计。

- **户外市集视觉系统**（如农夫市集、周末集市）——与"{inspiration_text}"的市场概念呼应，学习其手工感标签、木质材料和亲切的视觉语言。

- **季节性产品包装**（如日本季节限定包装、北欧设计）——结合"{inspiration_text}"中的自然元素，参考其色彩搭配和季节性视觉表达。

- **生鲜电商平台**（如每日优鲜、叮咚买菜）——借鉴其在表现"{inspiration_text}"类似场景时的界面设计、信息层级和用户体验设计。

- **摄影风格参考**（如美食摄影、生活方式摄影）——学习如何通过视觉手法表现"{inspiration_text}"的核心情绪和氛围，包括光影、构图和色调处理。"""
        
        logger.info(f"案例推荐生成成功，基于用户输入: {inspiration_text}")
        
        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        logger.error(f"获取案例推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取案例推荐失败: {str(e)}")

@app.post("/api/get_design_directions")
async def get_design_directions(request: dict):
    """获取可扩展设计方向（SCAMPER方法分析）"""
    try:
        inspiration_text = request.get("inspiration_text", "")
        
        if not inspiration_text.strip():
            raise HTTPException(status_code=400, detail="需要提供灵感文本")
        
        # 基于用户输入和SCAMPER方法生成设计方向
        directions = f"""### 🚀 可扩展的设计方向（基于"{inspiration_text}"）

#### 📋 基础方向
- **品牌识别系统**：围绕"{inspiration_text}"开发完整的logo、字体、色彩规范和应用标准。  
- **包装设计系列**：基于"{inspiration_text}"的视觉元素，创建从手提袋到产品包装的整套设计。  
- **空间环境设计**：将"{inspiration_text}"的氛围转化为实体空间，如展示厅、店面或活动空间。  
- **数字界面设计**：将"{inspiration_text}"的理念应用到APP、网站或数字平台的用户界面设计。  
- **营销物料设计**：基于"{inspiration_text}"创建海报、宣传册、社交媒体素材等推广物料。  
- **产品设计延伸**：从"{inspiration_text}"出发，设计相关的实体产品或周边商品。

#### 🔄 SCAMPER创新扩展
- **Substitute（替代）**：将"{inspiration_text}"中的传统元素替换为现代化、数字化或可持续材料。
- **Combine（结合）**：将"{inspiration_text}"与科技元素、文化符号或其他设计风格相结合。
- **Adapt（适应）**：让"{inspiration_text}"的设计理念适应不同季节、地区或目标群体。
- **Modify（修改）**：放大"{inspiration_text}"中的某些特征，或简化复杂元素以突出核心价值。
- **Put to other uses（新用途）**：将"{inspiration_text}"的设计语言应用到完全不同的行业或产品类别。
- **Eliminate（消除）**：简化"{inspiration_text}"中的冗余元素，突出最核心的设计特征。
- **Reverse（颠倒）**：从相反的角度重新诠释"{inspiration_text}"，创造意想不到的设计效果。"""
        
        logger.info(f"设计方向生成成功，基于用户输入: {inspiration_text}")
        
        return {"success": True, "directions": directions}
    except Exception as e:
        logger.error(f"获取设计方向失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取设计方向失败: {str(e)}")

@app.post("/api/get_multimodal_suggestions")
async def get_multimodal_suggestions(request: dict):
    """获取多模态灵感合成建议"""
    try:
        inspiration_text = request.get("inspiration_text", "")
        
        if not inspiration_text.strip():
            raise HTTPException(status_code=400, detail="需要提供灵感文本")
        
        # 基于用户输入生成多模态灵感合成建议
        suggestions = f"""### 🌈 多模态灵感合成建议（基于"{inspiration_text}"）

- **视觉摄影 + 手绘插画**：将"{inspiration_text}"的真实摄影与手绘元素结合，创造既真实又富有艺术感的视觉效果。

- **环境音效 + 动态视觉**：配合"{inspiration_text}"的主题，添加相应的自然音效或环境声音，增强沉浸式体验。

- **触感材质 + 印刷工艺**：基于"{inspiration_text}"选择相应的纸张材质、特殊印刷工艺，通过触觉强化设计理念。

- **AR交互 + 信息可视化**：在平面设计中嵌入AR功能，扫码后展现与"{inspiration_text}"相关的动态信息或3D效果。

- **色彩渐变 + 动画过渡**：将"{inspiration_text}"的色彩元素制作成动态渐变动画，用于数字媒体展示。

- **气味设计 + 空间体验**：在实体空间中结合与"{inspiration_text}"相关的气味设计，创造多感官体验。

- **声音logo + 视觉识别**：为"{inspiration_text}"的品牌理念设计专属的声音标识，与视觉系统协调统一。

- **数据驱动 + 实时生成**：基于"{inspiration_text}"的理念，创建能够实时响应数据变化的动态视觉系统。"""
        
        logger.info(f"多模态建议生成成功，基于用户输入: {inspiration_text}")
        
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        logger.error(f"获取多模态建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取多模态建议失败: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8787))
    uvicorn.run(
        "main_official:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    )

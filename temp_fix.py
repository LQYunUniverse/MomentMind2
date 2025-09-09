# 临时修复脚本
import re

def fix_file():
    # 读取文件
    with open('main_official_simple_memory_test.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复设计方向API - 删除重复和错误的部分
    # 找到设计方向函数的开始和结束
    start_pattern = r'@app\.post\("/api/get_design_directions"\)\s*async def get_design_directions.*?try:'
    end_pattern = r'raise HTTPException\(status_code=500, detail=f"获取设计方向失败: \{str\(e\)\}"\)'
    
    # 新的设计方向函数
    new_design_directions = '''@app.post("/api/get_design_directions")
async def get_design_directions(request: dict):
    """获取可扩展设计方向（SCAMPER方法分析）"""
    try:
        # 支持多种参数名称
        inspiration_text = (request.get("inspiration_text", "") or 
                           request.get("user_input", "") or
                           request.get("text", ""))
        
        # 如果文本为空，尝试使用最近的分析结果
        if not inspiration_text.strip():
            global last_analysis_result
            import time
            # 检查最近的分析结果（5分钟内有效）
            if (last_analysis_result["summary"] and 
                time.time() - last_analysis_result["timestamp"] < 300):
                inspiration_text = last_analysis_result["summary"]
                logger.info(f"设计方向使用最近的分析结果: {inspiration_text[:50]}...")
        
        if not inspiration_text.strip():
            logger.error(f"设计方向请求缺少文本参数，请求数据: {request}")
            raise HTTPException(status_code=400, detail="需要提供灵感文本")
        
        # 从分析结果中提取关键信息用于设计方向
        key_concepts = extract_keywords_for_search(inspiration_text)
        keywords_text = ", ".join(key_concepts[:3])  # 使用前3个关键词
        
        # 基于关键词生成设计方向
        directions = f"""### 设计方向推荐
基于关键概念: {keywords_text}

#### 基础应用方向
• 品牌识别系统: 开发包含logo、字体、色彩规范的完整视觉识别
• 包装设计系列: 创建从手提袋到产品包装的整套设计
• 空间环境设计: 将设计理念转化为展示厅、店面或活动空间
• 数字界面设计: 应用到APP、网站或数字平台的用户界面设计
• 营销物料设计: 创建海报、宣传册、社交媒体素材等推广物料
• 产品设计延伸: 设计相关的实体产品或周边商品

#### SCAMPER创新扩展
• Substitute(替代): 将传统元素替换为现代化、数字化或可持续材料
• Combine(结合): 与科技元素、文化符号或其他设计风格相结合
• Adapt(适应): 让设计理念适应不同季节、地区或目标群体
• Modify(修改): 放大某些特征，或简化复杂元素以突出核心价值
• Put to other uses(新用途): 将设计语言应用到完全不同的行业或产品类别
• Eliminate(消除): 简化冗余元素，突出最核心的设计特征
• Reverse(颠倒): 从相反的角度重新诠释，创造意想不到的设计效果

#### 具体实现建议
• 阶段一: 确定核心视觉元素和色彩体系
• 阶段二: 开发基础应用模板和规范文档
• 阶段三: 扩展到多媒介和跨平台应用
• 阶段四: 建立可持续的设计语言系统"""
        
        logger.info(f"设计方向生成成功，基于关键词: {keywords_text}")
        
        return {"success": True, "directions": directions}
    except Exception as e:
        logger.error(f"获取设计方向失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取设计方向失败: {str(e)}")'''
    
    # 使用正则表达式替换
    pattern = r'@app\.post\("/api/get_design_directions"\).*?raise HTTPException\(status_code=500, detail=f"获取设计方向失败: \{str\(e\)\}"\)'
    content = re.sub(pattern, new_design_directions, content, flags=re.DOTALL)
    
    # 修复多模态建议API
    new_multimodal = '''@app.post("/api/get_multimodal_suggestions")
async def get_multimodal_suggestions(request: dict):
    """获取多模态灵感合成建议"""
    try:
        # 支持多种参数名称
        inspiration_text = (request.get("inspiration_text", "") or 
                           request.get("user_input", "") or
                           request.get("text", ""))
        
        # 如果文本为空，尝试使用最近的分析结果
        if not inspiration_text.strip():
            global last_analysis_result
            import time
            # 检查最近的分析结果（5分钟内有效）
            if (last_analysis_result["summary"] and 
                time.time() - last_analysis_result["timestamp"] < 300):
                inspiration_text = last_analysis_result["summary"]
                logger.info(f"多模态建议使用最近的分析结果: {inspiration_text[:50]}...")
        
        if not inspiration_text.strip():
            logger.error(f"多模态建议请求缺少文本参数，请求数据: {request}")
            raise HTTPException(status_code=400, detail="需要提供灵感文本")
        
        # 从分析结果中提取关键信息用于多模态建议
        key_concepts = extract_keywords_for_search(inspiration_text)
        keywords_text = ", ".join(key_concepts[:3])  # 使用前3个关键词
        
        # 基于关键词生成多模态灵感合成建议
        suggestions = f"""### 多模态灵感合成建议
基于关键概念: {keywords_text}

#### 感官融合方案
• 视觉摄影 + 手绘插画: 真实摄影与手绘元素结合，创造艺术感视觉效果
• 环境音效 + 动态视觉: 配合主题添加自然音效，增强沉浸式体验
• 触感材质 + 印刷工艺: 选择相应纸张材质和特殊工艺，通过触觉强化理念
• 气味设计 + 空间体验: 实体空间结合相关气味设计，创造多感官体验

#### 技术融合方案
• AR交互 + 信息可视化: 平面设计嵌入AR功能，展现动态信息或3D效果
• 色彩渐变 + 动画过渡: 色彩元素制作动态渐变动画，用于数字媒体
• 声音logo + 视觉识别: 设计专属声音标识，与视觉系统协调统一
• 数据驱动 + 实时生成: 创建实时响应数据变化的动态视觉系统

#### 应用场景
• 品牌体验中心: 综合运用多种感官元素的沉浸式品牌展示
• 互动展览设计: 结合数字技术与物理空间的创新展示方式  
• 产品发布活动: 多模态元素协同的产品体验设计
• 教育培训环境: 多感官学习体验的空间与内容设计"""
        
        logger.info(f"多模态建议生成成功，基于关键词: {keywords_text}")
        
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        logger.error(f"获取多模态建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取多模态建议失败: {str(e)}")'''
    
    pattern2 = r'@app\.post\("/api/get_multimodal_suggestions"\).*?raise HTTPException\(status_code=500, detail=f"获取多模态建议失败: \{str\(e\)\}"\)'
    content = re.sub(pattern2, new_multimodal, content, flags=re.DOTALL)
    
    # 写回文件
    with open('main_official_simple_memory_test.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("文件修复完成!")

if __name__ == "__main__":
    fix_file()

/**
 * MomentMind 前端JavaScript应用
 * 多模态捕获和AI增强系统的前端交互逻辑
 */

class MomentMindApp {
    constructor() {
        this.selectedMethod = 'text';
        this.selectedFile = null;
        this.selectedImage = null;
        this.selectedImageData = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // 记录方式选择
        this.setupRecordingMethods();
        
        // 按钮事件
        document.getElementById('summarizeBtn').addEventListener('click', () => this.summarizeInspiration());
        document.getElementById('generateBtn').addEventListener('click', () => this.generateImage());
        document.getElementById('multimodalBtn').addEventListener('click', () => this.multimodalProcess());
        
        // 文件上传
        this.setupFileUpload();
        
        // 图片上传
        this.setupImageUpload();
        
        // 测试按钮
        this.setupTestButton();
    }

    setupRecordingMethods() {
        const methodCards = document.querySelectorAll('.method-card');
        methodCards.forEach(card => {
            card.addEventListener('click', () => {
                // 移除所有active类
                methodCards.forEach(c => c.classList.remove('active'));
                // 添加active类到当前卡片
                card.classList.add('active');
                // 更新选中的方法
                this.selectedMethod = card.dataset.method;
                
                // 显示/隐藏图片上传区域
                const imageUploadSection = document.getElementById('imageUploadSection');
                if (this.selectedMethod === 'image') {
                    imageUploadSection.style.display = 'block';
                } else {
                    imageUploadSection.style.display = 'none';
                }
                
                // 更新提示文本
                this.updatePlaceholderText();
            });
        });
    }

    updatePlaceholderText() {
        const textarea = document.getElementById('inspirationText');
        const placeholders = {
            'text': '记录您的设计灵感...',
            'image': '上传图片并可选择添加文字描述...',
            'ppg': '通过PPG/GSR生理信号触发捕获的灵感...',
            'audio': '音频录音转录的灵感内容...'
        };
        textarea.placeholder = placeholders[this.selectedMethod] || placeholders['text'];
    }

    setupFileUpload() {
        const fileUpload = document.getElementById('fileUpload');
        const fileInput = document.getElementById('fileInput');

        // 点击上传区域触发文件选择
        fileUpload.addEventListener('click', () => {
            fileInput.click();
        });

        // 文件选择事件
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // 拖拽事件
        fileUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUpload.classList.add('dragover');
        });

        fileUpload.addEventListener('dragleave', () => {
            fileUpload.classList.remove('dragover');
        });

        fileUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUpload.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            this.handleFileSelect(file);
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        this.selectedFile = file;
        const fileUpload = document.getElementById('fileUpload');
        
        // 更新上传区域显示
        fileUpload.innerHTML = `
            <i class="fas fa-check-circle" style="font-size: 3rem; color: #28a745; margin-bottom: 15px;"></i>
            <p><strong>已选择文件：</strong>${file.name}</p>
            <p style="font-size: 0.9rem; color: #666;">
                大小：${this.formatFileSize(file.size)} | 类型：${file.type}
            </p>
            <p style="font-size: 0.8rem; color: #667eea; margin-top: 10px; cursor: pointer;">
                点击重新选择文件
            </p>
        `;
    }

    setupImageUpload() {
        console.log('设置图片上传功能');
        
        // 避免重复绑定事件
        if (!this.imageUploadSetup) {
            this.imageUploadSetup = true;
            
            // 使用事件委托，监听整个文档的点击事件
            document.addEventListener('click', (e) => {
                // 检查是否点击了图片上传区域
                if (e.target.closest('#inspirationImageUpload')) {
                    console.log('检测到点击图片上传区域');
                    e.preventDefault();
                    const imageInput = document.getElementById('inspirationImageInput');
                    if (imageInput) {
                        console.log('触发文件选择');
                        imageInput.click();
                    } else {
                        console.error('未找到文件输入元素');
                    }
                }
            });
        }

        // 文件选择事件
        const imageInput = document.getElementById('inspirationImageInput');
        if (imageInput) {
            imageInput.addEventListener('change', (e) => {
                console.log('文件选择事件触发');
                this.handleImageSelect(e.target.files[0]);
            });
        }

        // 拖拽事件
        document.addEventListener('dragover', (e) => {
            const imageUpload = document.getElementById('inspirationImageUpload');
            if (imageUpload && e.target.closest('#inspirationImageUpload')) {
                e.preventDefault();
                imageUpload.classList.add('dragover');
            }
        });

        document.addEventListener('dragleave', (e) => {
            const imageUpload = document.getElementById('inspirationImageUpload');
            if (imageUpload && !e.target.closest('#inspirationImageUpload')) {
                imageUpload.classList.remove('dragover');
            }
        });

        document.addEventListener('drop', (e) => {
            const imageUpload = document.getElementById('inspirationImageUpload');
            if (imageUpload && e.target.closest('#inspirationImageUpload')) {
                e.preventDefault();
                imageUpload.classList.remove('dragover');
                const file = e.dataTransfer.files[0];
                this.handleImageSelect(file);
            }
        });
    }

    handleImageSelect(file) {
        if (!file) return;
        
        console.log('选择了文件:', file.name, file.type);
        
        // 检查文件类型
        if (!file.type.startsWith('image/')) {
            this.showAlert('请选择图片文件', 'warning');
            return;
        }

        this.selectedImage = file;
        
        // 读取图片并转换为base64
        const reader = new FileReader();
        reader.onload = (e) => {
            const fullDataUrl = e.target.result;
            this.selectedImageData = fullDataUrl.split(',')[1]; // 去掉data:image/...;base64,前缀
            
            console.log('图片读取成功，base64长度:', this.selectedImageData.length);
            
            // 更新上传区域显示，包含图片预览
            const imageUpload = document.getElementById('inspirationImageUpload');
            imageUpload.innerHTML = `
                <div style="text-align: center;">
                    <img src="${fullDataUrl}" alt="上传的图片" style="
                        max-width: 200px; 
                        max-height: 150px; 
                        border-radius: 8px; 
                        margin-bottom: 10px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    ">
                    <div>
                        <i class="fas fa-check-circle" style="color: #28a745; margin-right: 5px;"></i>
                        <strong>${file.name}</strong>
                    </div>
                    <p style="font-size: 0.8rem; color: #666; margin: 5px 0;">
                        大小：${this.formatFileSize(file.size)}
                    </p>
                    <p id="reselect-image" style="font-size: 0.8rem; color: #667eea; cursor: pointer; margin-top: 8px;">
                        <i class="fas fa-upload"></i> 点击重新选择图片
                    </p>
                </div>
            `;
            
            // 不需要重新绑定事件，因为我们使用了事件委托
            console.log('图片预览已更新，事件委托会自动处理点击');
            
            this.showAlert('图片上传成功！', 'success');
        };
        
        reader.onerror = () => {
            this.showAlert('图片读取失败，请重试', 'error');
        };
        
        reader.readAsDataURL(file);
    }

    setupTestButton() {
        // 避免重复绑定，使用单次事件监听
        if (!this.testButtonSetup) {
            this.testButtonSetup = true;
            document.addEventListener('click', (e) => {
                if (e.target.id === 'testUploadBtn') {
                    console.log('测试按钮被点击');
                    const imageInput = document.getElementById('inspirationImageInput');
                    if (imageInput) {
                        console.log('找到文件输入，触发点击');
                        imageInput.click();
                    } else {
                        console.error('未找到文件输入元素');
                    }
                }
            });
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async summarizeInspiration() {
        const text = document.getElementById('inspirationText').value.trim();
        const context = document.getElementById('contextText').value.trim();

        // 检查输入：文字或图片至少有一个
        if (!text && !this.selectedImageData) {
            this.showAlert('请输入灵感内容或上传图片', 'warning');
            return;
        }

        const btn = document.getElementById('summarizeBtn');
        const loading = document.getElementById('summarizeLoading');
        const result = document.getElementById('summarizeResult');
        
        try {
            // 显示加载状态
            btn.disabled = true;
            loading.style.display = 'block';
            result.classList.remove('show');

            const response = await fetch('/api/summarize_inspiration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text || '',
                    context: context,
                    recording_method: this.selectedMethod,
                    image_data: this.selectedImageData || null
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            console.log('API返回数据:', data);

            if (data.success) {
                console.log('AI分析结果:', data.summary);
                document.getElementById('summaryContent').innerHTML = `
                    <div style="white-space: pre-wrap; line-height: 1.6;">${data.summary}</div>
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; font-size: 0.9rem; color: #666;">
                        <strong>记录方式：</strong>${this.getMethodName(data.recording_method)}<br>
                        <strong>原始内容：</strong>${data.original_text.substring(0, 100)}${data.original_text.length > 100 ? '...' : ''}
                    </div>
                `;
                
                // 显示可展开模块
                const expandableModules = document.getElementById('expandableModules');
                if (expandableModules) {
                    expandableModules.style.display = 'block';
                    // 优先使用原始文本，如果没有则使用分析结果的摘要
                    const textForModules = data.original_text || data.summary || this.getTextInput();
                    this.setupExpandableModules(textForModules);
                }
                result.classList.add('show');
            } else {
                throw new Error(data.message || '处理失败');
            }

        } catch (error) {
            console.error('灵感总结失败:', error);
            this.showAlert(`灵感总结失败: ${error.message}`, 'error');
        } finally {
            btn.disabled = false;
            loading.style.display = 'none';
        }
    }

    async generateImage() {
        const prompt = document.getElementById('imagePrompt').value.trim();
        const style = document.getElementById('imageStyle').value;
        const size = document.getElementById('imageSize').value;

        if (!prompt) {
            this.showAlert('请输入图像描述', 'warning');
            return;
        }

        const btn = document.getElementById('generateBtn');
        const loading = document.getElementById('generateLoading');
        const result = document.getElementById('generateResult');
        
        try {
            btn.disabled = true;
            loading.style.display = 'block';
            result.classList.remove('show');

            const response = await fetch('/api/generate_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    style: style,
                    size: size
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                document.getElementById('imageContent').innerHTML = `
                    <img src="${data.image_url}" alt="Generated Image" class="generated-image">
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; font-size: 0.9rem; color: #666;">
                        <strong>原始提示：</strong>${data.original_prompt}<br>
                        <strong>优化提示：</strong>${data.revised_prompt}<br>
                        <strong>风格：</strong>${style} | <strong>尺寸：</strong>${size}
                    </div>
                `;
                result.classList.add('show');
            } else {
                throw new Error(data.message || '图像生成失败');
            }

        } catch (error) {
            console.error('图像生成失败:', error);
            this.showAlert(`图像生成失败: ${error.message}`, 'error');
        } finally {
            btn.disabled = false;
            loading.style.display = 'none';
        }
    }

    async multimodalProcess() {
        const text = document.getElementById('multimodalText').value.trim();
        const generateImage = document.getElementById('generateImageCheck').checked;

        if (!text && !this.selectedFile) {
            this.showAlert('请输入文本内容或上传文件', 'warning');
            return;
        }

        const btn = document.getElementById('multimodalBtn');
        const loading = document.getElementById('multimodalLoading');
        const result = document.getElementById('multimodalResult');
        
        try {
            btn.disabled = true;
            loading.style.display = 'block';
            result.classList.remove('show');

            // 创建FormData用于文件上传
            const formData = new FormData();
            formData.append('inspiration_text', text || '');
            formData.append('context', '');
            formData.append('recording_method', this.selectedMethod);
            formData.append('generate_image', generateImage);
            formData.append('image_style', 'vivid');
            
            if (this.selectedFile) {
                formData.append('uploaded_file', this.selectedFile);
            }

            const response = await fetch('/api/multimodal_inspiration', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                let resultHTML = '';
                
                // 显示总结结果
                if (data.multimodal_results.summary) {
                    resultHTML += `
                        <div style="margin-bottom: 25px;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">
                                <i class="fas fa-lightbulb"></i> AI灵感总结
                            </h4>
                            <div style="white-space: pre-wrap; line-height: 1.6; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                                ${data.multimodal_results.summary.summary}
                            </div>
                        </div>
                    `;
                }

                // 显示图像结果
                if (data.multimodal_results.image) {
                    resultHTML += `
                        <div style="margin-bottom: 25px;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">
                                <i class="fas fa-image"></i> 生成的图像
                            </h4>
                            <img src="${data.multimodal_results.image.image_url}" alt="Generated Image" class="generated-image">
                        </div>
                    `;
                }

                // 显示文件信息
                if (data.multimodal_results.uploaded_file) {
                    resultHTML += `
                        <div style="margin-bottom: 25px;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">
                                <i class="fas fa-file"></i> 上传的文件
                            </h4>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                                <strong>文件名：</strong>${data.multimodal_results.uploaded_file.filename}<br>
                                <strong>大小：</strong>${this.formatFileSize(data.multimodal_results.uploaded_file.size)}<br>
                                <strong>类型：</strong>${data.multimodal_results.uploaded_file.type}
                            </div>
                        </div>
                    `;
                }

                document.getElementById('multimodalContent').innerHTML = resultHTML;
                result.classList.add('show');
            } else {
                throw new Error(data.message || '多模态处理失败');
            }

        } catch (error) {
            console.error('多模态处理失败:', error);
            this.showAlert(`多模态处理失败: ${error.message}`, 'error');
        } finally {
            btn.disabled = false;
            loading.style.display = 'none';
        }
    }

    getMethodName(method) {
        const names = {
            'text': '文本记录',
            'image': '图片上传',
            'ppg': '生理信号',
            'audio': '音频录音'
        };
        return names[method] || method;
    }

    setupExpandableModules(inspirationText) {
        // 设置模块按钮点击事件
        const moduleButtons = document.querySelectorAll('.module-button');
        moduleButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                const module = e.currentTarget.dataset.module;
                const contentId = module === 'multimodal' ? 'multimodalSuggestionsContent' : `${module}Content`;
                const contentDiv = document.getElementById(contentId);
                
                if (contentDiv.classList.contains('show')) {
                    // 收起模块
                    contentDiv.classList.remove('show');
                    button.innerHTML = this.getModuleButtonHTML(module, false);
                } else {
                    // 展开模块
                    button.disabled = true;
                    button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> 加载中...`;
                    
                    try {
                        const content = await this.loadModuleContent(module, inspirationText);
                        contentDiv.innerHTML = content;
                        contentDiv.classList.add('show');
                        
                        // 更新按钮文本
                        button.innerHTML = this.getModuleButtonHTML(module, true);
                    } catch (error) {
                        contentDiv.innerHTML = `<p style="color: #dc3545;">加载失败: ${error.message}</p>`;
                        button.innerHTML = this.getModuleButtonHTML(module, false);
                    } finally {
                        button.disabled = false;
                    }
                }
            });
        });
    }

    getModuleButtonHTML(module, isExpanded) {
        const configs = {
            'cases': { 
                icon: 'fas fa-lightbulb', 
                text: '参考案例推荐' 
            },
            'directions': { 
                icon: 'fas fa-rocket', 
                text: '可扩展设计方向 (SCAMPER)' 
            },
            'multimodal': { 
                icon: 'fas fa-palette', 
                text: '多模态灵感合成建议' 
            }
        };
        
        const config = configs[module];
        const action = isExpanded ? '收起' : '查看';
        return `<i class="${config.icon}"></i> ${action}${config.text}`;
    }

    async loadModuleContent(module, inspirationText) {
        const endpoints = {
            'cases': '/api/get_case_recommendations',
            'directions': '/api/get_design_directions',
            'multimodal': '/api/get_multimodal_suggestions'
        };
        
        const response = await fetch(endpoints[module], {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                inspiration_text: inspirationText
            })
        });

        if (!response.ok) {
            throw new Error('网络请求失败');
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || '加载失败');
        }

        // 根据模块类型返回相应内容
        const contentKey = module === 'cases' ? 'recommendations' : 
                          module === 'directions' ? 'directions' : 'suggestions';
        
        return `<div style="white-space: pre-wrap; line-height: 1.6;">${data[contentKey]}</div>`;
    }

    getTextInput() {
        const method = this.selectedMethod;
        if (method === 'text') {
            return document.getElementById('inspirationText').value.trim();
        } else if (method === 'voice') {
            return document.getElementById('voiceText').value.trim();
        }
        return '';
    }

    showAlert(message, type = 'info') {
        // 创建临时提示元素
        const alert = document.createElement('div');
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            z-index: 10000;
            max-width: 400px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            animation: slideInRight 0.3s ease;
        `;

        // 根据类型设置颜色
        switch (type) {
            case 'error':
                alert.style.background = 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)';
                break;
            case 'warning':
                alert.style.background = 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)';
                break;
            case 'success':
                alert.style.background = 'linear-gradient(135deg, #27ae60 0%, #229954 100%)';
                break;
            default:
                alert.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }

        alert.textContent = message;
        document.body.appendChild(alert);

        // 3秒后自动移除
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 300);
            }
        }, 3000);

        // 添加动画样式
        if (!document.getElementById('alertStyles')) {
            const style = document.createElement('style');
            style.id = 'alertStyles';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    console.log('页面加载完成，初始化MomentMind应用');
    new MomentMindApp();
});

// 额外的调试：确保图片上传功能正常
window.addEventListener('load', () => {
    console.log('窗口完全加载，检查图片上传元素');
    
    // 直接绑定图片上传区域的点击事件
    setTimeout(() => {
        const imageUpload = document.getElementById('inspirationImageUpload');
        const imageInput = document.getElementById('inspirationImageInput');
        
        console.log('图片上传元素:', imageUpload);
        console.log('文件输入元素:', imageInput);
        
        if (imageUpload && imageInput) {
            imageUpload.style.border = '2px solid red'; // 临时红色边框用于调试
            imageUpload.addEventListener('click', function(e) {
                console.log('直接事件监听器被触发');
                e.preventDefault();
                imageInput.click();
            });
        }
    }, 1000);
});

// 添加一些辅助功能
window.addEventListener('load', () => {
    // 检查API健康状态
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            console.log('MomentMind API状态:', data);
        })
        .catch(error => {
            console.warn('API健康检查失败:', error);
        });
});

import React, { useState, useEffect, useRef } from 'react';
import { 
  Layers, 
  Sun, 
  ArrowRight, 
  MapPin, 
  Instagram, 
  Twitter, 
  Linkedin, 
  Menu, 
  X,
  Maximize2,
  Box,
  PenTool,
  Droplet,
  Cpu,
  Code,
  Aperture,
  MessageSquare,
  Send,
  Bot,
  User,
  Minimize2,
  Terminal,
  Download,
  Loader,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

// API 基础URL
const API_BASE_URL = 'http://localhost:5000/api';

// 论文中的示例图片（使用占位符，实际使用时可以替换为真实图片URL）
const PAPER_EXAMPLES = [
  {
    id: 1,
    title: "Dining Room",
    category: "Dining Room",
    image: "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    desc: "Procedurally generated dining room with realistic lighting and furniture arrangement."
  },
  {
    id: 2,
    title: "Bathroom",
    category: "Bathroom",
    image: "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    desc: "Fully procedural bathroom scene with detailed fixtures and materials."
  },
  {
    id: 3,
    title: "Living Room",
    category: "Living Room",
    image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    desc: "Modern living room with procedurally generated furniture and decorations."
  },
  {
    id: 4,
    title: "Kitchen",
    category: "Kitchen",
    image: "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    desc: "Kitchen scene with procedural cabinetry and appliances."
  }
];

// 更新为 Infinigen/室内生成相关的模拟数据
const PROJECTS = PAPER_EXAMPLES;

// --- 新增：AI 对话界面组件（连接后端API） ---
const ChatInterface = ({ onClose }) => {
  const [messages, setMessages] = useState([
    { id: 1, text: "Infinigen Core Online. version 2.5.1", sender: 'system' },
    { id: 2, text: "欢迎使用 Infinigen 场景生成系统。\n\n支持两种模式：\n1. 📋 模板模式（快速，2-3分钟）- 使用预生成模板\n2. 🏗️  生成模式（3-8分钟）- 生成全新场景，先预览后确认", sender: 'ai' }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [mode, setMode] = useState('template'); // 'template' 或 'generate'
  const messagesEndRef = useRef(null);
  const statusIntervalRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
    };
  }, []);

  // 轮询任务状态
  useEffect(() => {
    if (currentTaskId && (taskStatus?.status === 'running' || taskStatus?.status === 'rendering')) {
      statusIntervalRef.current = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/task/${currentTaskId}/status`);
          const data = await response.json();
          setTaskStatus(data);
          
          // 更新消息显示进度
          if (data.progress !== undefined) {
            const progressMsg = messages.find(m => m.id === 'progress');
            if (progressMsg) {
              setMessages(prev => prev.map(m => 
                m.id === 'progress' 
                  ? { ...m, text: `生成进度: ${data.progress}% - ${data.current_stage || data.message}` }
                  : m
              ));
            } else {
              setMessages(prev => [...prev, {
                id: 'progress',
                text: `生成进度: ${data.progress}% - ${data.current_stage || data.message}`,
                sender: 'ai'
              }]);
            }
          }
          
          // 如果完成，显示结果
          if (data.status === 'completed') {
            clearInterval(statusIntervalRef.current);
            
            // 检查是否需要确认（生成模式的预览）
            if (data.needs_confirmation && data.preview_image) {
              setMessages(prev => [...prev, {
                id: Date.now(),
                text: `✅ 场景布局已生成（见预览图）！\n\n是否需要精修渲染？`,
                sender: 'ai',
                taskData: data,
                needsConfirm: true
              }]);
            } else {
              // 已完成（模板模式或自动确认的生成模式）
              const modeText = data.mode === 'template' ? '模板模式' : '生成模式';
              const usedTemplate = data.used_template ? '（使用模板）' : '';
              setMessages(prev => [...prev, {
                id: Date.now(),
                text: `✅ ${modeText}完成${usedTemplate}！渲染图片已就绪。`,
                sender: 'ai',
                taskData: data
              }]);
            }
          } else if (data.status === 'rendering') {
            // 精修渲染中
            setMessages(prev => [...prev, {
              id: Date.now(),
              text: `🎨 正在进行精修渲染，请稍候...`,
              sender: 'ai'
            }]);
          } else if (data.status === 'failed') {
            clearInterval(statusIntervalRef.current);
            setMessages(prev => [...prev, {
              id: Date.now(),
              text: `❌ 生成失败: ${data.message}`,
              sender: 'ai'
            }]);
          }
        } catch (error) {
          console.error('获取任务状态失败:', error);
        }
      }, 2000); // 每2秒查询一次
    }
    
    return () => {
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
    };
  }, [currentTaskId, taskStatus?.status, messages]);

  const handleConfirmRender = async (taskId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/task/${taskId}/confirm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessages(prev => prev.map(msg => 
          msg.needsConfirm && msg.taskData?.task_id === taskId
            ? { ...msg, needsConfirm: false, text: `✅ 已确认，正在进行精修渲染...` }
            : msg
        ));
        // 重新开始轮询状态
        setTaskStatus({ status: 'rendering' });
      } else {
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: `❌ 确认失败: ${data.error || '未知错误'}`,
          sender: 'ai'
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `❌ 网络错误: ${error.message}`,
        sender: 'ai'
      }]);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { id: Date.now(), text: input, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    const userRequest = input;
    setInput("");
    setIsTyping(true);

    try {
      // 发送生成请求
      const modeText = mode === 'template' ? '模板模式' : '生成模式';
      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          request: userRequest,
          seed: null,
          mode: mode,
          auto_confirm: false  // 生成模式也先预览
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setCurrentTaskId(data.task_id);
        setTaskStatus(data);
        
        const aiMsg = {
          id: Date.now() + 1,
          text: `✅ 任务已创建（${modeText}）！任务ID: ${data.task_id}\n正在${mode === 'template' ? '检索模板并生成' : '生成场景'}，请稍候...`,
          sender: 'ai'
        };
        setMessages(prev => [...prev, aiMsg]);
      } else {
        const aiMsg = {
          id: Date.now() + 1,
          text: `❌ 错误: ${data.error || '生成请求失败'}`,
          sender: 'ai'
        };
        setMessages(prev => [...prev, aiMsg]);
      }
    } catch (error) {
      const aiMsg = {
        id: Date.now() + 1,
        text: `❌ 网络错误: ${error.message}`,
        sender: 'ai'
      };
      setMessages(prev => [...prev, aiMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[60] bg-slate-900 flex items-center justify-center p-4 animate-in fade-in duration-300">
      <div className="w-full max-w-4xl h-[85vh] bg-slate-950 rounded-2xl shadow-2xl border border-slate-800 flex flex-col overflow-hidden relative">
        
        {/* Header */}
        <div className="h-14 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="ml-4 font-mono text-sm text-indigo-400 flex items-center gap-2">
              <Terminal size={14} /> Infinigen_Terminal_v2
            </span>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-500 hover:text-white transition-colors p-2 hover:bg-slate-800 rounded-lg"
          >
            <Minimize2 size={20} />
          </button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 font-mono custom-scrollbar">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex max-w-[80%] gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                  msg.sender === 'user' ? 'bg-indigo-600' : 
                  msg.sender === 'system' ? 'bg-transparent' : 'bg-emerald-600'
                }`}>
                  {msg.sender === 'user' ? <User size={14} className="text-white"/> : 
                   msg.sender === 'system' ? null : <Bot size={14} className="text-white"/>}
                </div>

                {/* Bubble */}
                <div className={`p-4 rounded-xl text-sm leading-relaxed ${
                  msg.sender === 'user' ? 'bg-indigo-600/20 text-indigo-100 border border-indigo-500/30' : 
                  msg.sender === 'system' ? 'text-slate-500 text-xs italic w-full text-center' :
                  'bg-slate-800 text-slate-300 border border-slate-700'
                }`}>
                  <div className="whitespace-pre-wrap">{msg.text}</div>
                  
                  {/* 预览图片和确认按钮（生成模式） */}
                  {msg.needsConfirm && msg.taskData?.preview_image && (
                    <div className="mt-4 space-y-3">
                      <div>
                        <p className="text-xs text-slate-400 mb-2">预览图（快速预览）：</p>
                        <img 
                          src={`${API_BASE_URL}/task/${msg.taskData.task_id}/preview`}
                          alt="场景预览"
                          className="w-full rounded-lg border border-slate-600"
                        />
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleConfirmRender(msg.taskData.task_id)}
                          className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 text-sm flex items-center gap-2 transition-colors"
                        >
                          <CheckCircle size={14} />
                          确认并精修渲染
                        </button>
                        <a
                          href={`${API_BASE_URL}/task/${msg.taskData.task_id}/download/scene`}
                          download
                          className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 text-sm flex items-center gap-2 transition-colors"
                        >
                          <Download size={14} />
                          仅下载场景文件
                        </a>
                      </div>
                      <p className="text-xs text-slate-500">提示：精修渲染使用 Cycles 引擎，质量更高但需要约1分钟</p>
                    </div>
                  )}
                  
                  {/* 完成的结果展示 */}
                  {msg.taskData && msg.taskData.status === 'completed' && !msg.needsConfirm && (
                    <div className="mt-4 space-y-2">
                      {(msg.taskData.rendered_image || msg.taskData.preview_image) && (
                        <div>
                          <img 
                            src={`${API_BASE_URL}/task/${msg.taskData.task_id}/image`}
                            alt="生成的场景"
                            className="w-full rounded-lg mt-2"
                          />
                          <div className="flex gap-2 mt-2 flex-wrap">
                            <a
                              href={`${API_BASE_URL}/task/${msg.taskData.task_id}/download/scene`}
                              download
                              className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 text-xs flex items-center gap-1 transition-colors"
                            >
                              <Download size={12} />
                              下载场景文件
                            </a>
                            <a
                              href={`${API_BASE_URL}/task/${msg.taskData.task_id}/download/image`}
                              download
                              className="px-3 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 text-xs flex items-center gap-1 transition-colors"
                            >
                              <Download size={12} />
                              下载图片
                            </a>
                          </div>
                          {msg.taskData.mode === 'template' && msg.taskData.used_template && (
                            <p className="text-xs text-slate-500 mt-2">✨ 使用了模板池，快速生成</p>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 ml-11 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700/50">
                <Loader size={14} className="animate-spin text-emerald-500" />
                <span className="text-xs text-slate-400">处理中...</span>
              </div>
            </div>
          )}
          {(taskStatus && (taskStatus.status === 'running' || taskStatus.status === 'rendering')) && (
            <div className="flex justify-start">
              <div className="ml-11 bg-slate-800/50 px-4 py-3 rounded-xl border border-slate-700/50 max-w-md">
                <div className="flex items-center gap-2 mb-2">
                  <Loader size={14} className="animate-spin text-emerald-500" />
                  <span className="text-xs text-emerald-400 font-semibold">生成中...</span>
                </div>
                {taskStatus.progress !== undefined && (
                  <div className="mt-2">
                    <div className="w-full bg-slate-700 rounded-full h-2 mb-1">
                      <div 
                        className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${taskStatus.progress}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      {taskStatus.progress}% - {taskStatus.current_stage || taskStatus.message}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-slate-900 border-t border-slate-800">
          {/* 模式选择 */}
          <div className="mb-3 flex gap-2">
            <button
              onClick={() => setMode('template')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                mode === 'template'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              📋 模板模式（快速，2-3分钟）
            </button>
            <button
              onClick={() => setMode('generate')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                mode === 'generate'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              🏗️  生成模式（3-8分钟，预览+确认）
            </button>
          </div>
          
          <form onSubmit={handleSend} className="relative flex items-center gap-4">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 font-mono select-none">
              $ prompt:
            </div>
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入场景描述，例如：'生成一个北欧风格的卧室'"
              className="w-full bg-slate-950 text-white font-mono pl-24 pr-12 py-4 rounded-xl border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all placeholder:text-slate-600"
              autoFocus
            />
            <button 
              type="submit"
              disabled={!input.trim()}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={16} />
            </button>
          </form>
          <div className="text-center mt-2">
            <span className="text-[10px] text-slate-600 font-mono">
              Infinigen Indoors | API: {API_BASE_URL} | 
              模式: {mode === 'template' ? '模板（2-3分钟）' : '生成（3-8分钟）'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// 导航栏组件 (接受 toggleChat 属性)
const Navbar = ({ toggleChat }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed w-full z-50 transition-all duration-300 ${scrolled ? 'bg-white/80 backdrop-blur-md shadow-sm py-4' : 'bg-transparent py-6'}`}>
      <div className="container mx-auto px-6 flex justify-between items-center">
        <div className="flex items-center gap-2 cursor-pointer group">
          <div className="p-2 bg-indigo-600 rounded-lg text-white group-hover:rotate-12 transition-transform">
            <Cpu size={20} />
          </div>
          <span className={`text-xl font-bold tracking-tight ${scrolled ? 'text-slate-800' : 'text-slate-800'}`}>
            Infinigen<span className="text-indigo-600">Lab</span>.
          </span>
        </div>

        {/* Desktop Menu */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
          {['Scenes', 'Methodology', 'Dataset'].map((item) => (
            <a key={item} href={`#${item.toLowerCase()}`} className="hover:text-indigo-600 transition-colors relative group">
              {item}
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-indigo-600 transition-all duration-300 group-hover:w-full"></span>
            </a>
          ))}
          {/* 这里触发 Chat */}
          <button 
            onClick={toggleChat}
            className="px-5 py-2 bg-slate-900 text-white rounded-full hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-600/20 flex items-center gap-2"
          >
            <MessageSquare size={16} /> Let's Talk
          </button>
        </div>

        {/* Mobile Toggle */}
        <button onClick={() => setIsOpen(!isOpen)} className="md:hidden text-slate-800">
          {isOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden absolute top-full left-0 w-full bg-white border-b border-slate-100 p-6 flex flex-col gap-4 shadow-xl animate-in slide-in-from-top-5">
          {['Scenes', 'Methodology', 'Dataset'].map((item) => (
            <a key={item} href="#" className="text-lg font-medium text-slate-600" onClick={() => setIsOpen(false)}>
              {item}
            </a>
          ))}
          <button onClick={() => { toggleChat(); setIsOpen(false); }} className="text-lg font-medium text-indigo-600 text-left">
            Let's Talk
          </button>
        </div>
      )}
    </nav>
  );
};

// 英雄区域组件 (增加 Chat 按钮)
const Hero = ({ toggleChat }) => {
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    const { innerWidth, innerHeight } = window;
    const x = (e.clientX / innerWidth - 0.5) * 20;
    const y = (e.clientY / innerHeight - 0.5) * 20;
    setOffset({ x, y });
  };

  return (
    <header 
      className="relative min-h-screen flex items-center justify-center overflow-hidden bg-slate-50"
      onMouseMove={handleMouseMove}
    >
      <div 
        className="absolute top-20 right-0 w-[500px] h-[500px] bg-indigo-100/50 rounded-full blur-3xl opacity-60 pointer-events-none"
        style={{ transform: `translate(${offset.x * -1}px, ${offset.y * -1}px)` }}
      />
      <div 
        className="absolute bottom-0 left-20 w-[400px] h-[400px] bg-purple-100/50 rounded-full blur-3xl opacity-60 pointer-events-none"
        style={{ transform: `translate(${offset.x}px, ${offset.y}px)` }}
      />

      <div className="container mx-auto px-6 relative z-10 text-center">
        <span className="inline-block py-1 px-3 rounded-full bg-indigo-50 text-indigo-600 text-xs font-bold tracking-widest uppercase mb-6 animate-pulse">
          AI-Driven Spatial Generation
        </span>
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-slate-900 leading-tight mb-8">
          Infinite Interiors <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-500">
            Procedurally Real.
          </span>
        </h1>
        <p className="text-lg md:text-xl text-slate-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          Showcasing synthetic indoor scenes generated via Infinigen. 
          High-fidelity geometry, physically based materials, zero manual modeling.
        </p>
        
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <button 
            onClick={toggleChat}
            className="px-8 py-4 bg-slate-900 text-white rounded-full font-medium hover:bg-indigo-600 transition-colors flex items-center justify-center gap-2 group shadow-xl shadow-indigo-900/10"
          >
            <Terminal size={18} />
            Start AI Chat
          </button>
          <a 
            href="https://arxiv.org/pdf/2406.11824"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-4 bg-white text-slate-700 border border-slate-200 rounded-full font-medium hover:border-indigo-600 hover:text-indigo-600 transition-all shadow-sm inline-block"
          >
            Read Paper
          </a>
        </div>
      </div>

      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-slate-400 animate-bounce">
        <span className="text-xs uppercase tracking-widest">Scroll</span>
        <div className="w-px h-12 bg-gradient-to-b from-slate-400 to-transparent"></div>
      </div>
    </header>
  );
};

// ... (Portfolio, Features, Footer 组件保持不变，为了节省篇幅这里省略，但在实际合并时需要保留) ...
// 重新放入 Portfolio, Features, Footer 以确保文件完整性

const Portfolio = () => {
  const [filter, setFilter] = useState("All");
  const categories = ["All", "Living Room", "Kitchen", "Bedroom", "Details"];

  const filteredProjects = filter === "All" 
    ? PROJECTS 
    : PROJECTS.filter(p => p.category === filter);

  return (
    <section id="scenes" className="py-24 bg-white">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
          <div>
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Generated Results</h2>
            <div className="h-1 w-20 bg-indigo-500 rounded-full"></div>
            <p className="mt-4 text-slate-500">来自 Infinigen Indoors 论文的示例场景展示。</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                  filter === cat 
                    ? 'bg-slate-900 text-white shadow-lg' 
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredProjects.map((project) => (
            <div 
              key={project.id} 
              className="group relative cursor-pointer overflow-hidden rounded-2xl bg-slate-100 aspect-[4/5] md:aspect-[3/4]"
            >
              <img 
                src={project.image} 
                alt={project.title} 
                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-8">
                <div className="transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                  <span className="text-indigo-300 text-xs font-bold uppercase tracking-wider mb-2 block border border-indigo-300/30 inline-block px-2 py-1 rounded">
                    {project.category}
                  </span>
                  <h3 className="text-2xl font-bold text-white mb-2">{project.title}</h3>
                  <p className="text-slate-300 text-sm line-clamp-2">{project.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const Features = () => {
  const features = [
    {
      icon: <Code size={32} />,
      title: "100% Procedural",
      desc: "No manual modeling. Every mesh, texture, and layout is generated by code rules, ensuring infinite variety."
    },
    {
      icon: <Aperture size={32} />,
      title: "Photorealism",
      desc: "High-resolution geometry and physics-based rendering settings tuned for synthetic data training."
    },
    {
      icon: <Box size={32} />,
      title: "Semantic Annotation",
      desc: "Automatic generation of segmentation masks, depth maps, and object bounding boxes for CV tasks."
    }
  ];

  return (
    <section id="methodology" className="py-24 bg-slate-50 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent"></div>
      <div className="container mx-auto px-6">
        <div className="text-center mb-16 max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Why Synthetic Interiors?</h2>
          <p className="text-slate-500">Overcoming the data bottleneck in computer vision by creating diverse, labelled 3D environments.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {features.map((feature, idx) => (
            <div key={idx} className="bg-white p-10 rounded-3xl shadow-sm hover:shadow-xl transition-shadow duration-300 group border border-slate-100">
              <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center text-indigo-600 mb-6 group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-300">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-4">{feature.title}</h3>
              <p className="text-slate-500 leading-relaxed text-sm">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const Footer = () => {
  return (
    <footer className="bg-slate-900 text-white py-16">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-6">
              <Cpu className="text-indigo-400" size={24} />
              <span className="text-2xl font-bold">Infinigen<span className="text-indigo-400">Lab</span>.</span>
            </div>
            <p className="text-slate-400 max-w-sm mb-6">
              Exploring the frontiers of procedural generation for architectural interiors and computer vision.
            </p>
          </div>
          <div>
            <h4 className="font-bold text-lg mb-6">Resources</h4>
            <ul className="space-y-4 text-slate-400">
              <li>GitHub Repo</li>
              <li>Documentation</li>
              <li>Model Checkpoints</li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-lg mb-6">Lab</h4>
            <ul className="space-y-3 text-slate-400">
              <li>Team</li>
              <li>Publications</li>
              <li>Contact</li>
            </ul>
          </div>
        </div>
        <div className="pt-8 border-t border-slate-800 text-center text-slate-500 text-sm">
          © 2025 Infinigen Lab. Research purpose only.
        </div>
      </div>
    </footer>
  );
};

// Main App Component
export default function App() {
  const [showChat, setShowChat] = useState(false);

  // 禁止背景滚动当 Chat 打开时
  useEffect(() => {
    if (showChat) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
  }, [showChat]);

  return (
    <div className="font-sans text-slate-900 bg-white selection:bg-indigo-200 selection:text-indigo-900">
      <Navbar toggleChat={() => setShowChat(true)} />
      <Hero toggleChat={() => setShowChat(true)} />
      <Features />
      <Portfolio />
      <Footer />
      
      {/* 渲染对话框 */}
      {showChat && <ChatInterface onClose={() => setShowChat(false)} />}
    </div>
  );
}
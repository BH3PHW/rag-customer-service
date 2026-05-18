# RAG智能客服系统 - 第4章：前后端分离

## 🎯 本章目标

通过本章学习，你将：
- ✅ 理解什么是前后端分离
- ✅ 掌握API设计原则
- ✅ 学会前端如何调用API
- ✅ 理解数据流转过程

---

## 4.1 什么是前后端分离？

### 📖 定义

**前后端分离**是一种软件架构模式，将前端和后端作为独立的应用开发和部署。

### 🏗️ 架构对比

**传统单体架构：**
```
┌─────────────────────┐
│   HTML+CSS+Python   │
│    混合在一起       │
└─────────────────────┘
```

**前后端分离架构：**
```
┌──────────┐     ┌──────────┐
│  前端    │     │  后端    │
│ (React)  │────▶│(FastAPI) │
└──────────┘     └──────────┘
                     │
                ┌────┴────┐
                ▼         ▼
            PostgreSQL  Redis
```

### ✅ 前后端分离的好处

| 好处 | 说明 |
|------|------|
| **独立开发** | 前后端团队可以并行开发 |
| **技术灵活** | 前端可以选React/Vue，后端选Python/Go |
| **易于部署** | 前后端可以独立部署和扩展 |
| **更好的用户体验** | 前端可以实现更好的交互效果 |

---

## 4.2 API设计原则

### 📡 RESTful设计规范

**资源命名：**
- 使用名词表示资源
- 使用复数形式
- 避免使用动词

**正确示例：**
```
/api/v1/users          # 用户列表
/api/v1/users/{id}     # 单个用户
/api/v1/chat/sessions  # 会话列表
/api/v1/knowledge/documents  # 文档列表
```

**HTTP方法使用：**

| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 查询数据 | 获取用户列表 |
| POST | 创建数据 | 创建会话 |
| PUT | 更新数据 | 更新用户信息 |
| DELETE | 删除数据 | 删除会话 |

### 📝 API响应格式

```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "name": "张三",
    "email": "zhangsan@example.com"
  },
  "message": "操作成功",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**错误响应：**
```json
{
  "success": false,
  "error": {
    "code": "AUTH_FAILED",
    "message": "认证失败，请重新登录"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 🔐 认证机制

**JWT认证流程：**
```
用户登录 → 获取Token → 每次请求携带Token → 服务端验证Token
```

**请求头示例：**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 4.3 前端API调用

### 🔌 基础API调用

```javascript
// 封装API调用
const API_BASE_URL = 'http://localhost:8080';

async function fetchAPI(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    return await response.json();
}

// 使用示例
async function login(email, password) {
    const result = await fetchAPI('/api/v1/auth/login', 'POST', {
        email,
        password
    });
    
    if (result.success) {
        localStorage.setItem('token', result.data.token);
    }
    
    return result;
}

async function sendMessage(sessionId, message) {
    const token = localStorage.getItem('token');
    
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            sessionId,
            message
        })
    });
    
    return await response.json();
}
```

### ⚡ SSE流式输出

```javascript
// 流式聊天（打字机效果）
function streamChat(message) {
    const token = localStorage.getItem('token');
    
    // 使用EventSource接收流式数据
    const eventSource = new EventSource(
        `${API_BASE_URL}/api/v1/chat/stream`,
        {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }
    );
    
    // 发送消息
    fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message })
    });
    
    // 接收流式响应
    let responseText = '';
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        responseText += data.content;
        
        // 更新UI显示
        updateChatDisplay(responseText);
        
        if (data.done) {
            eventSource.close();
        }
    };
    
    eventSource.onerror = function() {
        eventSource.close();
    };
}
```

---

## 4.4 数据流转过程

### 🔄 完整数据流

```
用户发送消息
    │
    ▼
前端应用 (React)
    │
    ▼ (HTTP POST)
API网关 (认证、限流)
    │
    ▼
聊天服务 (RAG检索)
    │
    ├──► 向量数据库 (ChromaDB)
    │       │
    │       ▼ (语义检索)
    │   返回相似文档
    │       │
    │       ▼
    └──► LLM (生成回答)
            │
            ▼
        返回响应
            │
            ▼
        前端显示
```

### 📊 数据模型转换

**后端模型 → API响应 → 前端状态**

```python
# 后端模型 (SQLAlchemy)
class ChatMessage(Base):
    id = Column(String, primary_key=True)
    role = Column(String)
    content = Column(String)
    session_id = Column(String)
```

```json
// API响应
{
  "id": "msg-123",
  "role": "assistant",
  "content": "你好！我是智能客服",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

```javascript
// 前端状态 (Zustand)
const useChatStore = create((set) => ({
    messages: [],
    addMessage: (message) => set((state) => ({
        messages: [...state.messages, message]
    }))
}));
```

---

## 4.5 跨域问题

### 🔑 CORS配置

**后端配置（FastAPI）：**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**为什么需要CORS？**

浏览器有同源策略限制，防止恶意网站访问其他网站的数据。CORS告诉浏览器哪些请求是允许的。

---

## 🚀 动手练习

### 练习：创建前端聊天组件

1. 使用React创建一个聊天组件
2. 实现消息输入和发送功能
3. 调用后端API获取响应
4. 显示聊天历史

---

## 📝 本章总结

通过本章学习，你了解了：

1. **前后端分离概念** - 独立开发和部署
2. **API设计原则** - RESTful规范
3. **前端API调用** - fetch和SSE
4. **数据流转** - 从前端到后端再返回
5. **CORS配置** - 跨域问题解决

---

**下一章：[核心业务实现](05_implementation.md)**

# RAG智能客服系统 - 从入门到精通

## 🎯 课程目标

通过本课程，你将：
- ✅ 理解一个完整企业级项目的需求分析过程
- ✅ 掌握系统设计的抽象化方法
- ✅ 学会如何选择和应用技术栈
- ✅ 理解前后端分离架构
- ✅ 掌握核心业务的实现逻辑
- ✅ 能够独立阅读和修改项目代码

---

## 📚 课程大纲

| 章节 | 主题 | 核心内容 |
|------|------|----------|
| 第1章 | 需求分析 | 理解业务需求、用户角色、功能矩阵 |
| 第2章 | 系统设计 | 架构设计、抽象化、模块划分 |
| 第3章 | 技术栈详解 | Python、FastAPI、数据库、向量数据库 |
| 第4章 | 前后端分离 | API设计、数据流转、交互模式 |
| 第5章 | 核心业务实现 | RAG流程、聊天逻辑、安全防护 |
| 第6章 | 部署与运维 | Docker、容器化、监控 |

---

## 📖 第1章：需求分析

### 1.1 什么是需求分析？

需求分析就是搞清楚：**我们要做什么？为谁做？要达到什么目标？**

### 1.2 项目背景

想象一下，一家公司需要一个智能客服系统：
- 用户访问网站时，能随时咨询问题
- 企业可以管理自己的知识库
- 管理员可以管理整个平台

### 1.3 用户角色分析

| 角色 | 需求 | 期望功能 |
|------|------|----------|
| **消费者用户** | 快速获得问题答案 | 智能聊天、FAQ问答、转人工 |
| **企业管理员** | 管理企业客服配置 | 知识库管理、会话监控、敏感词设置 |
| **系统管理员** | 管理整个平台 | 租户管理、API配置、系统监控 |

### 1.4 功能矩阵

```
功能区域          | 消费者端 | 企业端 | 管理端
------------------|---------|--------|--------
智能聊天          | ✅      | ❌      | ❌
知识库查询        | ✅      | ✅      | ❌
会话历史          | ✅      | ✅      | ❌
知识库管理        | ❌      | ✅      | ❌
敏感词设置        | ❌      | ✅      | ❌
企业管理          | ❌      | ❌      | ✅
系统监控          | ❌      | ❌      | ✅
```

### 1.5 核心需求点

**业务需求：**
- 用户能与AI客服自然对话
- 支持知识库问答（RAG）
- 支持多渠道接入（网页、微信等）

**非业务需求：**
- 响应速度快（< 2秒）
- 支持流式输出（打字机效果）
- 安全防护（防注入攻击）
- 多租户隔离

---

## 📖 第2章：系统设计

### 2.1 什么是系统设计？

系统设计就是把需求转化为技术方案的过程。

### 2.2 架构设计

**为什么选择微服务架构？**

```
单体架构（不适合）              微服务架构（适合）
┌─────────────────────┐        ┌──────┐ ┌──────┐ ┌──────┐
│ 一个大程序           │        │用户  │ │聊天  │ │知识  │
│ 用户+聊天+知识库... │        │服务  │ │服务  │ │库服务│
└─────────────────────┘        └───┬──┘ └───┬──┘ └───┬──┘
                                    │       │       │
                                    └───────┴───────┘
                                              │
                                        [API网关]
```

### 2.3 模块划分

```
┌─────────────────────────────────────────────────────┐
│                     前端层                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐        │
│  │消费者端  │ │企业管理端│ │系统管理端    │        │
│  └────┬─────┘ └────┬─────┘ └──────┬───────┘        │
└───────┼────────────┼──────────────┼─────────────────┘
        │            │              │
        └────────────┴──────────────┘
                     │
┌─────────────────────────────────────────────────────┐
│                   API网关层                        │
│          [统一入口、路由转发、安全控制]              │
└──────────────────────────┬──────────────────────────┘
                          │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌───────────┐        ┌───────────┐        ┌───────────┐
│ 用户服务  │        │ 聊天服务  │        │ 知识库服务│
│ (认证)    │        │ (RAG)     │        │ (向量检索)│
└───────────┘        └───────────┘        └───────────┘
    │                      │                      │
    └──────────────────────┼──────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
         PostgreSQL              ChromaDB
         (关系数据)              (向量数据)
```

### 2.4 核心数据流

```
用户提问 → API网关 → 聊天服务 → 知识库检索 → LLM生成 → 返回回答
```

---

## 📖 第3章：技术栈详解

### 3.1 技术选型思考

为什么选这些技术？

| 技术 | 选择理由 | 替代方案 |
|------|----------|----------|
| Python | 生态丰富、AI友好、学习曲线平缓 | Go、Java |
| FastAPI | 高性能、自动文档、现代特性 | Flask、Django |
| PostgreSQL | 成熟稳定、支持复杂查询 | MySQL |
| Redis | 缓存、会话、限流 | Memcached |
| ChromaDB | 轻量级向量数据库 | Pinecone、Milvus |

### 3.2 Python基础回顾

```python
# 核心概念回顾
name = "智能客服"          # 变量
users = ["用户A", "用户B"] # 列表
config = {"host": "localhost"} # 字典

def chat(message):        # 函数
    return f"收到: {message}"

# 面向对象
class ChatSession:
    def __init__(self):
        self.messages = []
    
    def add_message(self, message):
        self.messages.append(message)
```

### 3.3 FastAPI核心概念

```python
from fastapi import FastAPI

app = FastAPI(title="智能客服API")

# 定义路由
@app.get("/")
async def root():
    return {"message": "欢迎使用智能客服"}

# 路径参数
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    return {"user_id": user_id}

# 请求体
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.post("/chat")
async def chat(request: ChatRequest):
    return {"response": f"你说: {request.message}"}
```

### 3.4 数据库基础

```python
# SQLAlchemy ORM
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 创建数据库连接
engine = create_engine("sqlite:///chat.db")
Session = sessionmaker(bind=engine)
db = Session()

# 定义模型
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
```

---

## 📖 第4章：前后端分离

### 4.1 什么是前后端分离？

```
传统方式（耦合）                    分离方式（解耦）
┌─────────────────────┐          ┌──────────┐     ┌──────────┐
│  HTML+CSS+Python    │          │  前端    │     │  后端    │
│  混在一起           │          │ (React)  │────▶│(FastAPI) │
└─────────────────────┘          └──────────┘     └──────────┘
                                                 │
                                            ┌────┴────┐
                                            ▼         ▼
                                        PostgreSQL  Redis
```

### 4.2 API设计原则

**RESTful设计规范：**

| 操作 | HTTP方法 | 路径示例 |
|------|----------|----------|
| 创建会话 | POST | /api/v1/chat/sessions |
| 发送消息 | POST | /api/v1/chat/sessions/{id}/messages |
| 获取历史 | GET | /api/v1/chat/sessions/{id} |
| 更新设置 | PUT | /api/v1/settings |
| 删除会话 | DELETE | /api/v1/chat/sessions/{id} |

### 4.3 前端API调用

```javascript
// 前端如何调用API
const API_BASE_URL = 'http://localhost:8080';

async function sendMessage(sessionId, message) {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            sessionId: sessionId,
            message: message
        })
    });
    return await response.json();
}
```

### 4.4 SSE流式输出

```javascript
// 流式聊天（打字机效果）
function streamChat(message) {
    const eventSource = new EventSource(
        `${API_BASE_URL}/api/v1/chat/stream?message=${message}`
    );
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        addToChat(data.content);
        
        if (data.done) {
            eventSource.close();
        }
    };
}
```

---

## 📖 第5章：核心业务实现

### 5.1 RAG流程详解

**RAG = 检索 + 生成**

```
用户提问 → 语义检索 → 知识库匹配 → LLM生成 → 返回回答
    │           │           │           │
    │           ▼           │           │
    │      向量化问题       │           │
    │           │           │           │
    │           ▼           │           │
    │      向量数据库查询    │           │
    │           │           │           │
    │           ▼           │           │
    │      找到相似文档      │           │
    │           │           │           │
    │           ▼           │           │
    │      构建Prompt       │           │
    │           │           │           │
    └───────────┴───────────┘           │
                                    ▼
                               LLM生成回答
```

### 5.2 核心代码实现

**聊天服务核心逻辑：**

```python
# backend/chat-service/main.py
from fastapi import FastAPI
from rag import retrieve_context, generate_response

app = FastAPI(title="聊天服务")

@app.post("/api/v1/chat/sessions")
async def chat(message: str, session_id: str | None = None):
    # 1. 检索知识库
    context = retrieve_context(message)
    
    # 2. 生成回答
    answer = generate_response(message, context)
    
    return {
        "success": True,
        "response": answer,
        "sources": context["sources"]
    }
```

**RAG检索实现：**

```python
# rag.py
import chromadb

def retrieve_context(query, top_k=3):
    """从向量数据库检索相关文档"""
    client = chromadb.Client()
    collection = client.get_collection("knowledge_base")
    
    # 查询相似文档
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    return {
        "documents": results["documents"][0],
        "sources": results["ids"][0]
    }
```

### 5.3 安全防护

**防提示词注入：**

```python
# prompt_injection_defender.py
def check_injection(message):
    """检测并防止提示词注入攻击"""
    dangerous_patterns = [
        "忽略之前的指令",
        "忘记你之前的身份",
        "扮演另一个角色",
        "执行以下代码"
    ]
    
    for pattern in dangerous_patterns:
        if pattern in message:
            return True, "检测到恶意输入"
    
    return False, None
```

---

## 📖 第6章：部署与运维

### 6.1 Docker容器化

**Dockerfile示例：**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**docker-compose.yml：**

```yaml
version: '3.8'
services:
  api-gateway:
    build: ./api-gateway
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: rag_db
  
  redis:
    image: redis:7
```

### 6.2 启动命令

```bash
# 开发环境
cd backend/api-gateway
uvicorn main:app --reload --port 8080

# 生产环境
docker-compose up -d
```

### 6.3 监控与日志

```bash
# 查看日志
docker-compose logs -f

# 健康检查
curl http://localhost:8080/health

# API文档
open http://localhost:8080/docs
```

---

## 🚀 动手实践

### 练习1：运行项目

```bash
# 1. 克隆仓库
git clone https://github.com/BH3PHW/rag-customer-service.git

# 2. 启动后端
cd rag-customer-service/backend
docker-compose up -d

# 3. 启动前端
git clone https://github.com/BH3PHW/rag-agent-frontend.git
cd rag-agent-frontend/apps/consumer
npm run dev
```

### 练习2：添加一个FAQ

修改 `backend/knowledge-service/main.py`，添加新的FAQ：

```python
@app.post("/api/v1/knowledge/faq")
async def add_faq(question: str, answer: str, category: str = "其他"):
    """添加FAQ"""
    # 实现逻辑
    pass
```

---

## 📋 学习检查清单

| 阶段 | 目标 | 状态 |
|------|------|------|
| 需求分析 | 理解三个用户角色的需求 | [ ] |
| 系统设计 | 理解微服务架构 | [ ] |
| 技术栈 | 会用FastAPI写API | [ ] |
| 前后端分离 | 理解API调用流程 | [ ] |
| 业务实现 | 理解RAG流程 | [ ] |
| 部署 | 能运行项目 | [ ] |

---

## 🎉 继续学习

现在你已经理解了整个项目的设计和实现，接下来可以：

1. **深入阅读源码**：从 `backend/api-gateway/main.py` 开始
2. **修改代码**：尝试添加一个新功能
3. **运行项目**：在本地搭建完整环境
4. **学习进阶内容**：RAG优化、性能调优、安全加固

---

**祝你学习愉快！🚀✨

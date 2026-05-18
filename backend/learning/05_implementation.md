# RAG智能客服系统 - 第5章：核心业务实现

## 🎯 本章目标

通过本章学习，你将：
- ✅ 理解RAG检索增强生成的完整流程
- ✅ 掌握聊天服务的核心逻辑
- ✅ 学会安全防护机制的实现
- ✅ 理解流式输出的实现方式

---

## 5.1 RAG流程详解

### 🧠 什么是RAG？

**RAG** (Retrieval-Augmented Generation) 是检索增强生成技术，结合了信息检索和大语言模型生成。

### 🔄 RAG完整流程

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

### 📝 RAG核心代码

```python
# backend/chat-service/rag.py
import chromadb
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

class RAGService:
    def __init__(self):
        # 初始化向量数据库
        self.client = chromadb.Client()
        self.collection = self.client.get_collection("knowledge_base")
        
        # 初始化LLM
        self.llm = OpenAI(temperature=0.7)
    
    def retrieve_context(self, query: str, top_k: int = 3) -> dict:
        """从知识库检索相关文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        return {
            "documents": results["documents"][0],
            "sources": results["ids"][0]
        }
    
    def generate_response(self, query: str, context: dict) -> str:
        """结合上下文生成回答"""
        # 构建Prompt
        prompt = f"""
        根据以下上下文信息回答问题：
        
        上下文：
        {context['documents']}
        
        问题：{query}
        
        请根据上下文回答问题，如果上下文没有相关信息，请说"我不太清楚"。
        """
        
        # 调用LLM
        response = self.llm(prompt)
        return response.strip()
    
    def chat(self, query: str) -> dict:
        """完整的RAG聊天流程"""
        # 1. 检索上下文
        context = self.retrieve_context(query)
        
        # 2. 生成回答
        answer = self.generate_response(query, context)
        
        return {
            "answer": answer,
            "sources": context["sources"],
            "context": context["documents"]
        }
```

---

## 5.2 聊天服务核心逻辑

### 📡 API实现

```python
# backend/chat-service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import RAGService
from sse_stream import ChatStreamer

app = FastAPI(title="聊天服务")

# 初始化RAG服务
rag_service = RAGService()

# 请求模型
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str

# 响应模型
class ChatResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    sources: list = []

# 同步聊天API
@app.post("/api/v1/chat/sessions", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """同步聊天API"""
    try:
        # 调用RAG服务
        result = rag_service.chat(request.message)
        
        return {
            "success": True,
            "response": result["answer"],
            "session_id": request.session_id or "new-session",
            "sources": result["sources"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 流式聊天API
@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天API（打字机效果）"""
    return ChatStreamer(request.message)
```

### ⚡ 流式输出实现

```python
# backend/chat-service/sse_stream.py
from fastapi import Response
import asyncio

class ChatStreamer:
    def __init__(self, message: str):
        self.message = message
    
    async def __aiter__(self):
        # 模拟流式输出
        responses = ["你", "好", "！", "我", "是", "智", "能", "客", "服", "。"]
        
        for char in responses:
            yield f"data: {char}\n\n"
            await asyncio.sleep(0.1)
        
        # 标记完成
        yield "data: [DONE]\n\n"

# 在FastAPI中使用
async def stream_response(message: str):
    """生成流式响应"""
    response = Response(
        content=generate_stream(message),
        media_type="text/event-stream"
    )
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    return response
```

---

## 5.3 安全防护机制

### 🛡️ 防提示词注入

```python
# backend/chat-service/prompt_injection_defender.py
import re

class PromptInjectionDefender:
    def __init__(self):
        # 危险模式列表
        self.dangerous_patterns = [
            r"忽略.*指令",
            r"忘记.*身份",
            r"扮演.*角色",
            r"执行.*代码",
            r"绕过.*限制",
            r"违反.*规则",
            r"请忘记",
            r"忽略以上",
            r"无视规则"
        ]
    
    def detect_injection(self, message: str) -> tuple:
        """检测提示词注入攻击"""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True, f"检测到恶意输入模式: {pattern}"
        
        return False, None
    
    def sanitize_input(self, message: str) -> str:
        """清理用户输入"""
        # 移除危险字符
        dangerous_chars = [";", "'", "\"", "`", "|", "&", "<", ">"]
        for char in dangerous_chars:
            message = message.replace(char, "")
        
        return message.strip()
```

### 🔐 SQL注入防护

```python
# 使用SQLAlchemy ORM自动防止SQL注入

# 安全的方式（使用ORM）
def get_user(db, user_id: int):
    # SQLAlchemy会自动转义参数
    return db.query(User).filter(User.id == user_id).first()

# 不安全的方式（手动拼接SQL）
def unsafe_get_user(db, user_id: int):
    # 危险！可能被SQL注入
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

### ⚙️ API限流

```python
# backend/api-gateway/rate_limiter.py
import redis
from fastapi import HTTPException

class RateLimiter:
    def __init__(self):
        self.redis = redis.Redis(host="localhost", port=6379, db=0)
        self.limit = 100  # 每分钟100次请求
    
    def check_limit(self, ip: str) -> bool:
        """检查IP是否超过限流"""
        key = f"rate_limit:{ip}"
        count = self.redis.incr(key)
        
        if count == 1:
            self.redis.expire(key, 60)  # 60秒过期
        
        if count > self.limit:
            return False
        
        return True
    
    def enforce_limit(self, ip: str):
        """强制执行限流"""
        if not self.check_limit(ip):
            raise HTTPException(
                status_code=429,
                detail="请求过于频繁，请稍后再试"
            )
```

---

## 5.4 会话管理

### 💬 会话存储

```python
# backend/chat-service/session_manager.py
import redis
import json
from datetime import timedelta

class SessionManager:
    def __init__(self):
        self.redis = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    
    def create_session(self, user_id: str) -> str:
        """创建新会话"""
        session_id = f"session_{user_id}_{int(time.time())}"
        
        session_data = {
            "user_id": user_id,
            "messages": [],
            "status": "active",
            "created_at": str(time.time())
        }
        
        self.redis.setex(
            f"session:{session_id}",
            timedelta(hours=24),
            json.dumps(session_data)
        )
        
        return session_id
    
    def get_session(self, session_id: str) -> dict | None:
        """获取会话信息"""
        data = self.redis.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return None
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到会话"""
        session = self.get_session(session_id)
        if session:
            session["messages"].append({
                "role": role,
                "content": content,
                "timestamp": str(time.time())
            })
            self.redis.setex(
                f"session:{session_id}",
                timedelta(hours=24),
                json.dumps(session)
            )
    
    def close_session(self, session_id: str):
        """关闭会话"""
        session = self.get_session(session_id)
        if session:
            session["status"] = "closed"
            self.redis.setex(
                f"session:{session_id}",
                timedelta(hours=24),
                json.dumps(session)
            )
```

---

## 🚀 动手练习

### 练习：实现一个简单的RAG聊天系统

1. 使用ChromaDB创建知识库
2. 添加一些FAQ文档
3. 实现简单的RAG检索
4. 使用OpenAI生成回答

---

## 📝 本章总结

通过本章学习，你了解了：

1. **RAG流程** - 检索增强生成的完整流程
2. **聊天服务** - 核心逻辑实现
3. **流式输出** - SSE实现打字机效果
4. **安全防护** - 防注入、限流等机制
5. **会话管理** - 使用Redis存储会话

---

**下一章：[部署与运维](06_deployment.md)**

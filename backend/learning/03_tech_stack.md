# RAG智能客服系统 - 第3章：技术栈详解

## 🎯 本章目标

通过本章学习，你将：
- ✅ 理解为什么选择这些技术
- ✅ 掌握Python和FastAPI的核心用法
- ✅ 学会使用数据库和向量数据库
- ✅ 理解项目中技术栈的应用

---

## 3.1 技术选型思考

### 🤔 为什么选择这些技术？

| 技术 | 选择理由 | 适用场景 |
|------|----------|----------|
| Python | 生态丰富、AI友好、学习曲线平缓 | 后端服务、数据处理 |
| FastAPI | 高性能、自动文档、现代特性 | Web API开发 |
| PostgreSQL | 成熟稳定、支持复杂查询 | 主数据存储 |
| Redis | 缓存、会话、限流 | 临时数据存储 |
| ChromaDB | 轻量级向量数据库 | 语义检索、RAG |
| React | 组件化、生态成熟 | 前端界面 |

### 🛠️ 技术栈全景图

```
前端层: React + TypeScript + Vite
    │
    ▼
API层: FastAPI
    │
    ▼
业务层: Python 微服务
    │
    ├──► PostgreSQL (关系数据)
    ├──► Redis (缓存/会话)
    └──► ChromaDB (向量数据)
```

---

## 3.2 Python基础

### 📦 核心概念

```python
# 1. 变量和数据类型
name = "智能客服"          # 字符串
age = 25                  # 整数
is_active = True          # 布尔值

# 2. 列表和字典
users = ["用户A", "用户B", "用户C"]  # 列表
config = {
    "host": "localhost",
    "port": 8080,
    "debug": True
}  # 字典

# 3. 函数
def greet(name):
    """打招呼函数"""
    return f"你好，{name}！"

# 4. 类和对象
class ChatMessage:
    def __init__(self, role, content):
        self.role = role      # "user" 或 "assistant"
        self.content = content
    
    def to_dict(self):
        return {"role": self.role, "content": self.content}

# 5. 条件和循环
if age >= 18:
    print("成年人")
else:
    print("未成年人")

for user in users:
    print(f"用户: {user}")
```

### 🚀 Python进阶

```python
# 1. 异步编程 (async/await)
async def fetch_data(url):
    """异步获取数据"""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# 2. 装饰器
def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"调用函数: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"函数返回: {result}")
        return result
    return wrapper

@log_decorator
def add(a, b):
    return a + b

# 3. 异常处理
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零！")
except Exception as e:
    print(f"发生错误: {e}")
```

---

## 3.3 FastAPI核心

### 🚀 创建第一个API

```python
# 安装依赖
# pip install fastapi uvicorn

from fastapi import FastAPI
from pydantic import BaseModel

# 创建应用实例
app = FastAPI(
    title="RAG智能客服API",
    description="智能客服系统的API接口",
    version="1.0.0"
)

# 定义数据模型
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str

class ChatResponse(BaseModel):
    success: bool
    response: str
    session_id: str

# 定义路由
@app.get("/")
async def root():
    """根路径"""
    return {"message": "欢迎使用RAG智能客服"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "api-gateway"}

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天API"""
    # 生成回复
    response = f"收到你的消息: {request.message}"
    
    return {
        "success": True,
        "response": response,
        "session_id": request.session_id or "new-session"
    }

# 运行命令: uvicorn main:app --reload --port 8080
```

### 🔌 请求参数

```python
from fastapi import Path, Query

# 路径参数
@app.get("/users/{user_id}")
async def get_user(user_id: str = Path(..., description="用户ID")):
    return {"user_id": user_id}

# 查询参数
@app.get("/search")
async def search(
    query: str = Query(..., description="搜索关键词"),
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量")
):
    return {"query": query, "page": page, "size": size}
```

### 📋 自动文档

FastAPI会自动生成API文档：
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

---

## 3.4 数据库操作

### 🗃️ SQLAlchemy ORM

```python
# 安装依赖
# pip install sqlalchemy

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 创建数据库连接
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. 定义模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)

# 3. 创建表
Base.metadata.create_all(bind=engine)

# 4. 操作数据库
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. CURD操作
def create_user(db, email: str, name: str, password: str):
    hashed_password = password + "hash"  # 简化示例
    user = User(email=email, name=name, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

### ⚡ Redis缓存

```python
# 安装依赖
# pip install redis

import redis

# 连接Redis
r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

# 基本操作
r.set("key", "value")
value = r.get("key")

# 设置过期时间（10秒）
r.setex("temp_code", 10, "123456")

# 哈希操作
r.hset("user:1", mapping={
    "name": "张三",
    "email": "zhangsan@example.com"
})
user = r.hgetall("user:1")

# 列表操作
r.lpush("chat_history", "你好")
history = r.lrange("chat_history", 0, -1)
```

---

## 3.5 向量数据库

### 🧠 ChromaDB入门

```python
# 安装依赖
# pip install chromadb

import chromadb
from chromadb.utils import embedding_functions

# 1. 创建客户端
client = chromadb.Client()

# 2. 创建集合
collection = client.create_collection("knowledge_base")

# 3. 添加文档
documents = [
    "产品支持7天无理由退货",
    "配送时间通常为24小时",
    "客服工作时间是9:00-18:00"
]
collection.add(
    documents=documents,
    ids=["doc1", "doc2", "doc3"]
)

# 4. 语义搜索
results = collection.query(
    query_texts=["如何退货"],
    n_results=2
)

print("搜索结果:")
for i, doc in enumerate(results["documents"][0]):
    print(f"{i+1}. {doc}")
```

---

## 🚀 动手练习

### 练习：创建一个简单的FAQ服务

1. 使用FastAPI创建一个FAQ API
2. 使用SQLite存储FAQ数据
3. 支持添加、查询FAQ
4. 使用Redis缓存热门查询

---

## 📝 本章总结

通过本章学习，你了解了：

1. **技术选型** - 为什么选择这些技术
2. **Python基础** - 核心语法和进阶特性
3. **FastAPI** - 创建高性能API
4. **数据库** - SQLAlchemy和Redis
5. **向量数据库** - ChromaDB语义检索

---

**下一章：[前后端分离](04_separation.md)**

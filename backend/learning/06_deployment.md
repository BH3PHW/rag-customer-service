# RAG智能客服系统 - 第6章：部署与运维

## 🎯 本章目标

通过本章学习，你将：
- ✅ 理解Docker容器化
- ✅ 学会使用Docker Compose部署
- ✅ 掌握环境配置方法
- ✅ 了解监控和日志管理

---

## 6.1 Docker容器化

### 🐳 什么是Docker？

**Docker**是一种容器化技术，可以将应用和依赖打包在一起，实现一致的运行环境。

### 🔧 Docker基本概念

| 概念 | 说明 |
|------|------|
| **Image（镜像）** | 应用的打包模板 |
| **Container（容器）** | 镜像运行的实例 |
| **Dockerfile** | 定义如何构建镜像 |
| **Docker Compose** | 编排多个容器 |

### 📦 Dockerfile示例

```dockerfile
# backend/api-gateway/Dockerfile
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 📝 多阶段构建优化

```dockerfile
# 构建阶段
FROM python:3.10-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 生产阶段
FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## 6.2 Docker Compose部署

### 🤝 docker-compose.yml

```yaml
version: '3.8'

services:
  # API网关
  api-gateway:
    build: ./api-gateway
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/rag_db
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # 用户服务
  user-service:
    build: ./user-service
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/rag_db
    depends_on:
      - postgres
    restart: unless-stopped

  # 聊天服务
  chat-service:
    build: ./chat-service
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/rag_db
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # 知识库服务
  knowledge-service:
    build: ./knowledge-service
    ports:
      - "8003:8003"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # PostgreSQL数据库
  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=rag_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 🚀 启动命令

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

---

## 6.3 环境配置

### 🔧 .env文件

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/rag_db
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM配置
OPENAI_API_KEY=sk-your-api-key
LLM_PROVIDER=openai

# 安全配置
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
API_RATE_LIMIT=100

# 日志配置
LOG_LEVEL=INFO
```

### 📝 配置加载

```python
# backend/api-gateway/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "postgresql://user:password@localhost:5432/rag_db"
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT配置
    jwt_secret_key: str = "secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # LLM配置
    openai_api_key: str = ""
    llm_provider: str = "openai"
    
    # 安全配置
    cors_origins: list = ["http://localhost:3000"]
    api_rate_limit: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 6.4 服务器部署

### 🖥️ 服务器准备

```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt-get install docker-compose -y

# 验证安装
docker --version
docker-compose --version
```

### 🚀 部署步骤

```bash
# 1. 克隆仓库
git clone https://github.com/BH3PHW/rag-customer-service.git
cd rag-customer-service

# 2. 创建.env文件
cp .env.example .env
# 编辑.env文件，填入真实配置

# 3. 启动服务
docker-compose up -d

# 4. 验证服务
curl http://localhost:8080/health
```

### 🔒 安全配置

```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# 安装SSL证书（使用Let's Encrypt）
sudo apt-get install certbot nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 6.5 监控与日志

### 📊 日志管理

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api-gateway
docker-compose logs -f chat-service

# 查看最近100行日志
docker-compose logs --tail=100 api-gateway

# 导出日志到文件
docker-compose logs api-gateway > api-gateway.log
```

### 🔍 健康检查

```python
# backend/api-gateway/main.py
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/health")
async def system_health():
    """系统健康检查"""
    services = [
        {"name": "api-gateway", "status": "healthy"},
        {"name": "user-service", "status": "healthy"},
        {"name": "chat-service", "status": "healthy"},
        {"name": "knowledge-service", "status": "healthy"}
    ]
    
    return {
        "status": "healthy" if all(s["status"] == "healthy" for s in services) else "degraded",
        "services": services,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 📈 指标监控

```bash
# 查看容器资源使用
docker stats

# 查看网络情况
docker network inspect rag-customer-service_default

# 查看存储使用
docker system df
```

---

## 🚀 动手练习

### 练习：部署项目到服务器

1. 在云服务器上安装Docker和Docker Compose
2. 克隆项目仓库
3. 配置环境变量
4. 启动服务
5. 验证服务正常运行

---

## 📝 本章总结

通过本章学习，你了解了：

1. **Docker容器化** - 创建镜像和容器
2. **Docker Compose** - 编排多个服务
3. **环境配置** - .env文件和配置加载
4. **服务器部署** - 在生产环境部署
5. **监控与日志** - 查看日志和健康检查

---

## 🎉 课程结束

恭喜你完成了整个RAG智能客服系统的学习课程！

### 📋 学习成果

你现在可以：
- ✅ 理解需求分析过程
- ✅ 设计系统架构
- ✅ 使用Python和FastAPI
- ✅ 实现前后端分离
- ✅ 实现RAG核心逻辑
- ✅ 部署项目到服务器

### 🚀 下一步

1. **深入源码** - 阅读项目中的真实代码
2. **添加功能** - 尝试实现新功能
3. **优化性能** - 学习性能调优
4. **参与开源** - 贡献代码

---

**祝你在技术道路上越走越远！🚀✨**

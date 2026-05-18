# RAG智能客服系统 - 前端应用

## 项目简介

RAG智能客服系统前端应用，包含三个独立的前端项目，采用React+TypeScript+Vite技术栈。支持消费者端、企业管理端、系统管理端三个用户角色。

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **状态管理**: Zustand (轻量级)
- **UI组件**: 自定义组件 (无第三方库依赖)
- **API通信**: Fetch API
- **包管理**: npm workspaces

## 应用结构

```
frontend/
├── apps/
│   ├── consumer/          # 消费者端 (3001)
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── api/client.ts
│   │   │   └── pages/Chat.tsx
│   │   └── package.json
│   ├── enterprise/        # 企业管理端 (3002)
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── api/client.ts
│   │   │   └── pages/
│   │   │       ├── KnowledgeBase.tsx
│   │   │       ├── ChatMonitor.tsx
│   │   │       ├── SensitiveSettings.tsx
│   │   │       ├── Channels.tsx
│   │   │       └── Settings.tsx
│   │   └── package.json
│   └── system-admin/      # 系统管理端 (3003)
│       ├── src/
│       │   ├── App.tsx
│       │   └── pages/
│       │       ├── Tenants.tsx
│       │       ├── Users.tsx
│       │       ├── ApiConfig.tsx
│       │       ├── ModelConfig.tsx
│       │       └── Services.tsx
│       └── package.json
├── docs/                 # 文档
│   ├── deployment.md    # 部署指南
│   └── api-testing.md   # API测试指南
├── tests/                # 测试
│   └── debug_frontend.js
└── package.json
```

## 快速开始

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0

### 安装依赖

```bash
# 安装所有应用的依赖
npm install
```

### 启动开发服务器

**方式一：分别启动各应用**
```bash
# 消费者端 (3001)
cd apps/consumer
npm run dev

# 企业端 (3002)
cd apps/enterprise
npm run dev

# 系统管理端 (3003)
cd apps/system-admin
npm run dev
```

## 各应用功能

### 消费者端 (Consumer)
- 🎨 浮动客服聊天窗口
- 💬 实时智能对话
- ⚡ SSE流式输出 (打字机效果)
- 📱 响应式设计，支持移动端

访问地址: http://localhost:3001

### 企业管理端 (Enterprise)
- 📊 会话监控与管理
- 📚 知识库管理（文档上传、编辑）
- 🔌 渠道接入管理
- 🛡️ 敏感词与安全设置
- 👥 团队成员管理
- 📈 数据统计与分析

访问地址: http://localhost:3002

### 系统管理端 (System Admin)
- 🏢 企业租户管理
- 👤 用户管理
- ⚙️ API配置与模型配置
- 📊 系统监控与状态
- 💾 存储配置
- 🔧 系统设置

访问地址: http://localhost:3003

## 生产构建

```bash
# 构建所有应用
npm run build

# 或构建单个应用
npm run build --workspace=apps/consumer
npm run build --workspace=apps/enterprise
npm run build --workspace=apps/system-admin
```

## 环境变量

创建 `.env` 文件:

```env
# API Gateway地址
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080

# 应用环境
NEXT_PUBLIC_APP_ENV=development
```

---

## 前后端联合调试

### 前置条件

1. 确保已克隆两个仓库:
   - 前端: `https://github.com/BH3PHW/rag-agent-frontend`
   - 后端: `https://github.com/BH3PHW/rag-customer-service`

### 完整开发流程

#### 1. 先启动后端服务

```bash
# 进入后端目录
cd ../backend

# 启动 API Gateway (8080)
cd api-gateway
uvicorn main:app --reload --port 8080
```

验证后端启动成功:
- 访问 http://localhost:8080/health
- 访问 http://localhost:8080/docs (API文档)

#### 2. 配置前端API地址

检查并确保前端API配置指向本地后端:

编辑 `apps/[app-name]/src/api/client.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8080';
```

#### 3. 启动前端应用

打开新的终端窗口:

```bash
# 消费者端 (3001)
cd apps/consumer
npm run dev

# (另开终端) 企业端 (3002)
cd apps/enterprise
npm run dev

# (另开终端) 系统管理端 (3003)
cd apps/system-admin
npm run dev
```

#### 4. 验证联合调试

访问以下地址:
- 消费者端: http://localhost:3001
- 企业端: http://localhost:3002
- 系统管理端: http://localhost:3003
- API文档: http://localhost:8080/docs

### 使用前端调试脚本

运行联合调试测试:

```bash
cd tests

# 完整调试 (所有应用)
node debug_frontend.js --all

# 调试单个应用
node debug_frontend.js --consumer
node debug_frontend.js --enterprise
node debug_frontend.js --admin
```

调试内容:
- 消费者端: 聊天、知识库测试
- 企业端: 登录、会话、知识库管理测试
- 系统管理端: 系统管理功能测试
- API匹配度验证

---

## 前后端联合部署

### 完整部署架构

```
┌─────────────────────────────────────────────────────┐
│              CDN/负载均衡 (Vercel/Nginx)           │
└────────────┬────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌─────▼─────┐
│ 前端   │      │  后端     │
│ 部署   │      │  部署     │
└───┬────┘      └─────┬─────┘
    │                 │
┌───▼────────────┐  ┌─▼───────────┐
│ consumer 3001  │  │ API GW 8080 │
│ enterprise 3002│  │ 微服务集群  │
│ system-admin  │  └─────────────┘
└───────────────┘
```

### 生产部署方案

#### 方案一：Vercel部署前端 + Docker部署后端

**前端部署到Vercel**
```bash
# 1. 推送代码到 GitHub
git push origin main

# 2. 在 Vercel 中导入项目并配置环境变量
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
```

**后端部署到Docker**
```bash
cd backend
docker-compose up -d
```

#### 方案二：Nginx部署前端和后端

**前端Nginx配置**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 消费者端
    location / {
        root /var/www/frontend/apps/consumer/dist;
        try_files $uri $uri/ /index.html;
    }

    # 企业端
    location /enterprise {
        alias /var/www/frontend/apps/enterprise/dist;
        try_files $uri $uri/ /enterprise/index.html;
    }

    # 管理端
    location /admin {
        alias /var/www/frontend/apps/system-admin/dist;
        try_files $uri $uri/ /admin/index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 生产环境变量配置

**后端环境变量**
```env
DATABASE_URL=postgresql://user:pass@production-db/rag_db
REDIS_URL=redis://production-redis:6379/0
JWT_SECRET_KEY=your-secure-production-key
OPENAI_API_KEY=sk-production-key
CORS_ORIGINS=["https://your-domain.com"]
```

**前端环境变量**
```env
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
NEXT_PUBLIC_APP_ENV=production
```

### 部署验证清单

部署完成后，请检查以下项目:

- [ ] 所有前端应用可正常访问
- [ ] API Gateway 健康检查通过
- [ ] API 文档可正常访问
- [ ] 前后端通信正常
- [ ] 聊天功能正常工作
- [ ] 流式输出正常
- [ ] 知识库功能正常
- [ ] 认证功能正常
- [ ] HTTPS证书配置正确
- [ ] 日志与监控正常

---

## 文档与资源

- [部署指南](./docs/deployment.md) - 详细的部署说明
- [API测试指南](./docs/api-testing.md) - API测试用例和调试方法
- [后端仓库](https://github.com/BH3PHW/rag-customer-service) - 后端服务代码
- [联合调试报告](../backend/tests/api-joint-debug-report.md) - 前后端联调报告

## 开发指南

### 添加新页面

1. 在 `apps/[app-name]/src/pages/` 目录创建新的React组件
2. 在 `App.tsx` 中添加路由和菜单
3. 在 `api/client.ts` 中添加相应的API调用函数

### 调试技巧

- 打开浏览器开发者工具 (F12)
- 查看Console中的API请求和响应
- 使用Network标签查看请求详情
- 检查是否有CORS错误或API地址错误

## 许可证

MIT License

# 前端部署指南

## 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0
- Git

## 安装依赖

```bash
# 安装所有工作区依赖
npm install

# 或仅安装特定应用的依赖
cd apps/consumer && npm install
cd apps/enterprise && npm install
cd apps/system-admin && npm install
```

## 开发环境运行

### 消费者端应用 (浮动客服窗口)

```bash
cd apps/consumer
npm run dev
```

访问地址：`http://localhost:3001`

### 企业管理端应用

```bash
cd apps/enterprise
npm run dev
```

访问地址：`http://localhost:3002`

### 系统管理端应用

```bash
cd apps/system-admin
npm run dev
```

访问地址：`http://localhost:3003`

## 生产环境构建

### 构建所有应用

```bash
npm run build
```

### 构建单个应用

```bash
npm run build --workspace=apps/consumer
npm run build --workspace=apps/enterprise
npm run build --workspace=apps/system-admin
```

## 环境变量配置

创建 `.env.local` 文件：

```env
# API Gateway 地址
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080

# 应用特定配置
NEXT_PUBLIC_APP_ENV=development
```

### 生产环境变量

```env
# 生产环境 API 地址
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com

# 生产环境标识
NEXT_PUBLIC_APP_ENV=production
```

## 部署到不同平台

### 部署到 Vercel

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel
```

### 部署到 Nginx

1. 构建应用：
```bash
npm run build
```

2. 配置 Nginx：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 消费者端
    location / {
        root /path/to/frontend/apps/consumer/out;
        try_files $uri $uri/ /index.html;
    }
    
    # 企业管理端
    location /enterprise {
        alias /path/to/frontend/apps/enterprise/out;
        try_files $uri $uri/ /enterprise/index.html;
    }
    
    # 系统管理端
    location /admin {
        alias /path/to/frontend/apps/system-admin/out;
        try_files $uri $uri/ /admin/index.html;
    }
}
```

### 部署到 Docker

创建 `Dockerfile`：

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/apps/consumer/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## API 配置

### 开发环境

前端默认连接本地 API Gateway：

```javascript
// apps/consumer/src/config/api.ts
export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080',
  timeout: 30000,
  retry: 3
};
```

### 生产环境

确保设置正确的 API 地址：

```bash
# 使用环境变量
export NEXT_PUBLIC_API_BASE_URL=https://api.production.com
```

## 常见问题

### 1. CORS 错误

确保 API Gateway 配置了正确的 CORS 头：

```python
# backend/api-gateway/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. API 请求超时

调整超时配置：

```javascript
const client = createClient({
  baseURL: API_CONFIG.baseURL,
  timeout: 60000  // 60秒超时
});
```

### 3. 构建失败

清理缓存后重试：

```bash
rm -rf node_modules .next
npm install
npm run build
```

## 验证部署

部署完成后，访问以下地址验证：

- 消费者端：`http://your-domain.com/`
- 企业管理端：`http://your-domain.com/enterprise`
- 系统管理端：`http://your-domain.com/admin`

## 后续维护

- 定期更新依赖：`npm update`
- 监控错误日志
- 定期备份配置

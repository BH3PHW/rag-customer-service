# 前端API测试指南

## 测试环境准备

### 1. 启动后端服务

确保后端所有服务已启动：

```bash
# 启动 API Gateway
cd backend/api-gateway
uvicorn main:app --reload --port 8080

# 启动其他微服务（可选，用于完整测试）
```

### 2. 启动前端应用

```bash
# 启动消费者端
cd apps/consumer
npm run dev

# 或启动所有应用
npm run dev --workspace=apps/consumer
```

## API测试用例

### 消费者端 API 测试

#### 1. 发送聊天消息

**请求：**
```http
POST /api/v1/chat/sessions
Content-Type: application/json

{
  "message": "你好，我想咨询产品问题"
}
```

**预期响应：**
```json
{
  "success": true,
  "data": {
    "sessionId": "uuid-string",
    "messages": [
      {
        "id": "msg-uuid",
        "role": "user",
        "content": "你好，我想咨询产品问题",
        "timestamp": "2024-01-01T10:00:00Z"
      },
      {
        "id": "msg-uuid-2",
        "role": "assistant",
        "content": "您好！有什么可以帮助您的吗？",
        "timestamp": "2024-01-01T10:00:01Z"
      }
    ]
  }
}
```

#### 2. 流式聊天 (SSE)

**请求：**
```http
POST /api/v1/chat/stream
Content-Type: application/json

{
  "message": "详细介绍你们的AI客服",
  "sessionId": "existing-session-id"
}
```

**预期响应：**
```
data: {"content": "您好", "done": false}
data: {"content": "，我们的", "done": false}
data: {"content": "AI客服系统", "done": false}
data: {"content": "采用先进的", "done": false}
...
data: {"content": "RAG技术。", "done": true}
```

### 企业管理端 API 测试

#### 1. 用户登录

**请求：**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@company.com",
  "password": "password123"
}
```

**预期响应：**
```json
{
  "success": true,
  "data": {
    "token": "jwt-token-string",
    "user": {
      "id": "user-uuid",
      "email": "admin@company.com",
      "role": "enterprise_admin"
    }
  }
}
```

#### 2. 获取会话列表

**请求：**
```http
GET /api/v1/chat/sessions
Authorization: Bearer <token>
```

**预期响应：**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "session-uuid",
        "visitorId": "visitor-id",
        "status": "active",
        "messageCount": 5,
        "createdAt": "2024-01-01T10:00:00Z",
        "lastMessage": "有什么可以帮助您的？"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}
```

### 系统管理端 API 测试

#### 1. 获取系统统计

**请求：**
```http
GET /api/v1/admin/stats
Authorization: Bearer <admin-token>
```

**预期响应：**
```json
{
  "success": true,
  "data": {
    "totalEnterprises": 50,
    "totalUsers": 1000,
    "totalSessions": 50000,
    "totalMessages": 200000,
    "activeConnections": 150
  }
}
```

#### 2. API 配置管理

**请求：**
```http
GET /api/v1/admin/api-config
Authorization: Bearer <admin-token>
```

**预期响应：**
```json
{
  "success": true,
  "data": {
    "configs": [
      {
        "id": "config-uuid",
        "name": "OpenAI",
        "type": "llm",
        "enabled": true,
        "settings": {
          "model": "gpt-4",
          "temperature": 0.7
        }
      }
    ]
  }
}
```

## 测试脚本使用

### 运行所有测试

```bash
# 设置环境变量
export API_BASE_URL=http://localhost:8080
export API_KEY=your-api-key

# 运行测试脚本
node tests/debug_frontend.js --all
```

### 运行特定应用测试

```bash
# 仅测试消费者端
node tests/debug_frontend.js --consumer

# 仅测试企业管理端
node tests/debug_frontend.js --enterprise

# 仅测试系统管理端
node tests/debug_frontend.js --admin
```

## 前端功能测试检查清单

### 消费者端 (浮动客服窗口)

- [ ] 客服窗口能够正常打开/关闭
- [ ] 消息能够正常发送和接收
- [ ] 流式输出显示正常（打字机效果）
- [ ] 历史消息能够正确加载
- [ ] 连接状态指示器正常
- [ ] 错误提示能够正确显示

### 企业管理端

- [ ] 登录功能正常
- [ ] 会话列表加载正常
- [ ] 会话详情能够查看
- [ ] 知识库管理正常
- [ ] 敏感词设置正常
- [ ] 统计数据加载正常

### 系统管理端

- [ ] 系统管理员登录正常
- [ ] 企业管理功能正常
- [ ] API配置管理正常
- [ ] 用户管理正常
- [ ] 系统统计显示正常

## 性能测试

### 响应时间测试

| 操作 | 预期响应时间 | 最大可接受时间 |
|------|-------------|---------------|
| 页面加载 | < 2s | 5s |
| API请求 | < 500ms | 2s |
| 流式响应 | < 1s (首字) | 3s |
| 消息发送 | < 300ms | 1s |

### 并发测试

```bash
# 使用 Apache Bench 进行并发测试
ab -n 100 -c 10 -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/v1/chat/sessions
```

## 故障排查

### 问题：请求返回 401 未授权

**可能原因：**
- Token 过期
- Token 未正确传递
- 权限不足

**解决方案：**
1. 检查 Authorization 头
2. 刷新 token
3. 检查用户权限

### 问题：请求返回 429 限流

**可能原因：**
- 请求频率过高
- IP 被限制

**解决方案：**
1. 降低请求频率
2. 等待限流时间过期
3. 联系管理员调整限流配置

### 问题：CORS 错误

**可能原因：**
- API Gateway 未配置 CORS
- 前端地址未在白名单中

**解决方案：**
1. 检查后端 CORS 配置
2. 确保前端地址在 allow_origins 中

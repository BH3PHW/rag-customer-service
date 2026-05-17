
# RAG Agent 前端

一个通用的 RAG (检索增强生成) Agent 前端应用，支持文档管理和智能问答。

## 功能特性

- 🤖 **智能聊天**: 与 AI 对话，支持 Markdown 渲染
- 📄 **文档管理**: 支持拖拽上传，多种文档格式
- ⚙️ **灵活配置**: 可自定义 API 密钥、模型参数等
- 💾 **本地存储**: 数据自动保存到浏览器本地存储
- 🐳 **Docker 支持**: 一键部署

## 快速开始

### 使用 Docker (推荐)

```bash
# 构建并启动
docker-compose up -d

# 访问 http://localhost:3000
```

### 本地开发

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建生产版本
pnpm build
```

## 项目结构

```
/workspace
├── src/
│   ├── pages/          # 页面组件
│   ├── types.ts        # TypeScript 类型定义
│   ├── store.ts        # Zustand 状态管理
│   └── App.tsx         # 主应用组件
├── Dockerfile          # Docker 配置
├── docker-compose.yml  # Docker Compose 配置
└── nginx.conf          # Nginx 配置
```

## 技术栈

- React 18 + TypeScript
- Vite
- Tailwind CSS
- Zustand
- Lucide Icons
- React Markdown

## License

MIT

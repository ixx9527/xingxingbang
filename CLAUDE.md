# 星星榜项目

## 部署方式

项目通过 Git 推送后在阿里云 ECS 上以 Docker 方式部署。

### 部署命令

```bash
cd /path/to/xingxingbang && git pull && docker compose up -d --build
```

### 服务说明

| 服务 | 容器名称 | 端口 | 说明 |
|------|----------|------|------|
| backend | xingxingbang-backend | 8000 | FastAPI 后端 |
| web | xingxingbang-web | 80 | Vue 3 前端 (nginx) |

### 数据持久化

- 数据目录: `./data`
- 数据库文件: `./data/xingxingbang.db`

### 架构

- 前端使用 nginx 部署静态文件，并代理 `/api` 请求到后端
- 后端 FastAPI 提供 REST API
- 数据库使用 SQLite
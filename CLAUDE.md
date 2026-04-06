# 星星榜项目

## 部署方式

项目通过 Git 推送后在阿里云 ECS 上以 Docker 方式部署。

### 部署命令

```bash
cd /path/to/xingxingbang && git pull && docker compose up -d --build backend
```

### 说明

- 项目使用 `docker-compose.yml` 管理容器
- 后端服务名称: `backend`，容器名称: `xingxingbang-backend`
- 数据持久化目录: `./data`
- 后端端口: `8000`
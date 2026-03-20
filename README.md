# ⭐ 星星榜 - 儿童成长打卡系统

儿童日常行为记录与积分打卡系统，支持微信小程序和Web管理后台。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Vue](https://img.shields.io/badge/Vue-3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ 功能特性

- 📱 **微信小程序** - 孩子打卡、查看积分、完成任务
- 🖥️ **Web管理后台** - 家长管理、数据统计
- ⭐ **积分等级系统** - 10个等级，从萌芽宝宝到宇宙星神
- 🔑 **邀请码注册** - 家长生成邀请码，控制注册权限
- 📊 **数据统计** - 积分趋势、分类统计、历史记录
- 🐳 **群晖部署** - Docker一键部署

## 🏗️ 技术架构

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.10 + FastAPI + SQLite |
| 小程序 | 微信原生开发 |
| Web前台 | Vue 3 + Element Plus |
| 部署 | Docker + Docker Compose |

## 📁 项目结构

```
xingxingbang/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── main.py         # FastAPI 入口
│   │   ├── models.py       # 数据库模型
│   │   ├── schemas.py      # 数据模型
│   │   ├── crud.py         # 业务逻辑
│   │   ├── security.py     # 认证
│   │   └── config.py       # 配置
│   ├── requirements.txt
│   └── Dockerfile
│
├── miniprogram/            # 微信小程序
│   └── src/
│       ├── pages/
│       │   ├── login/      # 登录
│       │   ├── register/    # 注册
│       │   ├── index/      # 首页打卡
│       │   ├── stats/      # 统计
│       │   ├── tasks/      # 任务管理
│       │   └── profile/    # 个人中心
│       ├── app.js
│       └── app.json
│
├── docker-compose.yml       # Docker 编排
└── .env.example            # 环境变量示例
```

## 🚀 快速开始

### 1. 克隆项目

```bash
cd /volume1/docker
git clone git@github.com:ixx9527/xingxingbang.git
cd xingxingbang
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env
```

修改 `SECRET_KEY`：
```bash
# 生成密钥
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 访问服务

| 服务 | 地址 |
|------|------|
| Web后台 | http://群晖IP:3000 |
| API | http://群晖IP:8000 |
| 健康检查 | http://群晖IP:8000/health |

## 📱 微信小程序配置

### 1. 修改API地址

编辑 `miniprogram/app.js`：
```javascript
globalData: {
  apiBase: 'http://你的服务器IP:8000'
}
```

### 2. 配置合法域名

在微信公众平台后台配置：
- request合法域名：`http://你的服务器IP:8000`

## 🔑 邀请码使用

1. 首次登录Web后台
2. 进入「邀请码管理」
3. 生成邀请码（设置使用次数、有效期）
4. 将邀请码分享给需要注册的用户

## ⭐ 等级系统

| 等级 | 名称 | 所需积分 | 标志 |
|------|------|----------|------|
| 1 | 萌芽宝宝 | 0 | 🌱 |
| 2 | 小小星 | 50 | 🌟 |
| 3 | 闪亮星 | 150 | ✨ |
| 4 | 智慧星 | 300 | 🧠 |
| 5 | 勇敢星 | 500 | ⚡ |
| 6 | 全能星 | 800 | 🏆 |
| 7 | 超级星 | 1200 | 🚀 |
| 8 | 传奇星 | 1800 | 👑 |
| 9 | 至尊星 | 2500 | 💎 |
| 10 | 宇宙星神 | 3500 | 🌌 |

## 📋 预设行为

### 学习类
| 行为 | 积分 |
|------|------|
| 阅读30分钟 | +3 |
| 数学口算完成 | +2 |
| 数学口算错一题 | -1 |
| 英语朗读 | +3 |
| 练琴30分钟 | +3 |
| 完成作业 | +5 |

### 生活习惯类
| 行为 | 积分 |
|------|------|
| 早起不赖床 | +2 |
| 自己整理房间 | +3 |
| 按时睡觉 | +2 |
| 挑食/剩饭 | -2 |

### 运动类
| 行为 | 积分 |
|------|------|
| 户外运动1小时 | +5 |
| 跳绳500个 | +3 |
| 游泳 | +5 |

## 🐳 群晖部署

### 端口规划

| 端口 | 用途 |
|------|------|
| 3000 | Web管理后台 |
| 8000 | API服务 |

### 备份

```bash
# 备份数据库
cp data/xingxingbang.db backup/xingxingbang_$(date +%Y%m%d).db
```

### 更新

```bash
cd /volume1/docker/xingxingbang
docker-compose down
git pull
docker-compose build
docker-compose up -d
```

## 📄 API接口

### 认证
- `POST /api/auth/login` - 登录
- `POST /api/auth/register` - 注册（需邀请码）
- `GET /api/invite-codes` - 获取邀请码列表
- `POST /api/invite-codes` - 生成邀请码

### 孩子
- `GET /api/children` - 获取孩子列表
- `POST /api/children` - 添加孩子
- `GET /api/children/{id}` - 获取孩子详情

### 行为
- `GET /api/behaviors` - 获取行为列表
- `POST /api/behaviors` - 创建行为
- `PUT /api/behaviors/{id}` - 更新行为
- `DELETE /api/behaviors/{id}` - 删除行为

### 打卡
- `POST /api/children/{id}/records` - 添加打卡
- `GET /api/children/{id}/records` - 获取记录

### 统计
- `GET /api/children/{id}/scores` - 积分统计
- `GET /api/children/{id}/scores/chart` - 趋势图
- `GET /api/children/{id}/level` - 等级信息

## 📝 许可证

MIT License

---

Made with ❤️ by 星星榜
# 星星榜 API 文档

**版本：** 1.0.0  
**描述：** 儿童成长打卡系统后端 API

---

## 目录

- [概述](#概述)
- [认证说明](#认证说明)
- [API 列表](#api-列表)
  - [健康检查](#健康检查)
  - [认证接口](#认证接口)
  - [邀请码接口](#邀请码接口)
  - [孩子接口](#孩子接口)
  - [行为接口](#行为接口)
  - [打卡记录接口](#打卡记录接口)
  - [积分统计接口](#积分统计接口)
  - [等级接口](#等级接口)
  - [用户接口](#用户接口)

---

## 概述

### 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `/api` |
| 认证方式 | Bearer Token (JWT) |
| 数据格式 | JSON |

### 公共响应头

```
Content-Type: application/json
```

---

## 认证说明

除健康检查和部分公开接口外，大多数接口需要在请求头中携带 JWT Token：

```
Authorization: Bearer <your_access_token>
```

### Token 获取

通过 [登录](#用户登录) 或 [注册](#用户注册) 接口获取 access_token。

### Token 有效期

- 默认有效期：30 分钟
- 过期后需重新登录

---

## API 列表

### 健康检查

#### 健康检查

检查服务运行状态。

**请求**

```
GET /health
```

**请求参数：** 无

**请求头：** 无特殊要求

**响应示例**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 服务状态 (ok/error) |
| version | string | 应用版本 |

---

### 认证接口

#### 用户注册

创建新用户账号（需要邀请码）。

**请求**

```
POST /api/auth/register
```

**请求参数 (Body)**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| nickname | string | 是 | 昵称 |
| invite_code | string | 是 | 邀请码 |

**请求示例**

```json
{
  "username": "testuser",
  "password": "password123",
  "nickname": "测试用户",
  "invite_code": "ABC123"
}
```

**请求头：** 无

**响应示例**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| access_token | string | JWT 访问令牌 |
| token_type | string | Token 类型 (bearer) |

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 400 | 用户名已存在 / 邀请码无效 / 邀请码已过期 / 邀请码已达到使用上限 |

---

#### 用户登录

用户登录获取 Token。

**请求**

```
POST /api/auth/login
```

**请求参数 (Body)**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**

```json
{
  "username": "testuser",
  "password": "password123"
}
```

**请求头：** 无

**响应示例**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| access_token | string | JWT 访问令牌 |
| token_type | string | Token 类型 (bearer) |

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 401 | 用户名或密码错误 |

---

### 邀请码接口

所有邀请码接口需要 **Bearer Token 认证**。

#### 获取邀请码列表

获取当前用户创建的所有邀请码。

**请求**

```
GET /api/invite-codes
```

**请求参数：** 无

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
[
  {
    "id": 1,
    "code": "ABC123",
    "max_uses": 5,
    "used_count": 2,
    "expires_at": "2026-05-03T12:00:00",
    "is_active": true,
    "note": "给孩子妈妈的邀请码",
    "created_at": "2026-04-03T12:00:00"
  }
]
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 邀请码 ID |
| code | string | 邀请码字符串 |
| max_uses | integer | 最大使用次数 |
| used_count | integer | 已使用次数 |
| expires_at | datetime | 过期时间 |
| is_active | boolean | 是否激活 |
| note | string | 备注 |
| created_at | datetime | 创建时间 |

---

#### 创建邀请码

生成新的邀请码。

**请求**

```
POST /api/invite-codes
```

**请求参数 (Body)**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| max_uses | integer | 否 | 1 | 最大使用次数 |
| days_valid | integer | 否 | 30 | 有效期（天） |
| note | string | 否 | - | 备注 |

**请求示例**

```json
{
  "max_uses": 5,
  "days_valid": 60,
  "note": "给孩子妈妈的邀请码"
}
```

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "id": 2,
  "code": "XYZ789",
  "max_uses": 5,
  "used_count": 0,
  "expires_at": "2026-06-02T12:00:00",
  "is_active": true,
  "note": "给孩子妈妈的邀请码",
  "created_at": "2026-04-03T12:00:00"
}
```

---

#### 删除邀请码

删除指定的邀请码。

**请求**

```
DELETE /api/invite-codes/{code_id}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code_id | integer | 邀请码 ID |

**请求参数：** 无

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "message": "删除成功"
}
```

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 404 | 邀请码不存在 |

---

### 孩子接口

所有孩子接口需要 **Bearer Token 认证**。

#### 获取孩子列表

获取当前用户的所有孩子。

**请求**

```
GET /api/children
```

**请求参数：** 无

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
[
  {
    "id": 1,
    "name": "小明",
    "birth_date": "2020-01-15",
    "gender": "male",
    "avatar": "/avatars/boy1.png",
    "total_points": 256.5,
    "streak_days": 15
  }
]
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 孩子 ID |
| name | string | 姓名 |
| birth_date | string | 出生日期 |
| gender | string | 性别 (male/female) |
| avatar | string | 头像 URL |
| total_points | float | 总积分 |
| streak_days | integer | 连续打卡天数 |

---

#### 添加孩子

创建新的孩子记录。

**请求**

```
POST /api/children
```

**请求参数 (Body)**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 姓名 |
| birth_date | string | 否 | 出生日期 (YYYY-MM-DD) |
| gender | string | 否 | 性别 (male/female) |
| avatar | string | 否 | 头像 URL |

**请求示例**

```json
{
  "name": "小明",
  "birth_date": "2020-01-15",
  "gender": "male",
  "avatar": "/avatars/boy1.png"
}
```

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "id": 1,
  "name": "小明",
  "birth_date": "2020-01-15",
  "gender": "male",
  "avatar": "/avatars/boy1.png",
  "total_points": 0,
  "streak_days": 0
}
```

---

#### 获取孩子详情

获取指定孩子的详细信息。

**请求**

```
GET /api/children/{child_id}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| child_id | integer | 孩子 ID |

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "id": 1,
  "name": "小明",
  "birth_date": "2020-01-15",
  "gender": "male",
  "avatar": "/avatars/boy1.png",
  "total_points": 256.5,
  "streak_days": 15,
  "created_at": "2026-01-01T10:00:00"
}
```

**响应字段**

在孩子列表响应基础上增加：

| 字段 | 类型 | 说明 |
|------|------|------|
| created_at | datetime | 创建时间 |

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 404 | 孩子不存在或不属于当前用户 |

---

### 行为接口

#### 获取行为列表

获取所有行为模板（支持按分类筛选）。

**请求**

```
GET /api/behaviors
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 行为分类（学习/生活习惯/运动/其他） |

**请求示例**

```
GET /api/behaviors?category=学习
```

**请求头：** 无（公开接口）

**响应示例**

```json
[
  {
    "id": 1,
    "name": "阅读 30 分钟",
    "points": 3,
    "category": "学习",
    "icon": "📚",
    "description": "",
    "is_system": true
  },
  {
    "id": 6,
    "name": "完成作业",
    "points": 5,
    "category": "学习",
    "icon": "✏️",
    "description": "",
    "is_system": true
  }
]
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 行为 ID |
| name | string | 行为名称 |
| points | float | 基础分值 |
| category | string | 分类 |
| icon | string | 图标 |
| description | string | 描述 |
| is_system | boolean | 是否系统预设（系统预设不能删除/编辑） |

---

#### 创建自定义行为

创建新的自定义行为。

**请求**

```
POST /api/behaviors
```

**请求参数 (Body)**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 行为名称 |
| points | float | 是 | 分值 |
| category | string | 是 | 分类 |
| icon | string | 否 | 图标 |
| description | string | 否 | 描述 |

**请求示例**

```json
{
  "name": "练习书法",
  "points": 4,
  "category": "学习",
  "icon": "🖌️",
  "description": "每天练习书法 30 分钟"
}
```

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "id": 20,
  "name": "练习书法",
  "points": 4,
  "category": "学习",
  "icon": "🖌️",
  "description": "每天练习书法 30 分钟",
  "is_system": false
}
```

---

#### 更新行为

更新指定的自定义行为。

**请求**

```
PUT /api/behaviors/{behavior_id}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| behavior_id | integer | 行为 ID |

**请求参数 (Body)**

同 [创建行为](#创建自定义行为) 参数。

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "id": 20,
  "name": "练习书法",
  "points": 5,
  "category": "学习",
  "icon": "🖌️",
  "description": "每天练习书法 30 分钟",
  "is_system": false
}
```

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 400 | 系统预设行为不能编辑 |

---

#### 删除行为

删除指定的自定义行为。

**请求**

```
DELETE /api/behaviors/{behavior_id}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| behavior_id | integer | 行为 ID |

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "message": "删除成功"
}
```

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 400 | 系统预设行为不能删除 |

---

### 打卡记录接口

所有打卡记录接口需要 **Bearer Token 认证**。

#### 添加打卡记录

为指定孩子添加一条打卡记录。

**请求**

```
POST /api/children/{child_id}/records
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| child_id | integer | 孩子 ID |

**请求参数 (Body)**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| behavior_id | integer | 是 | - | 行为 ID |
| points | float | 是 | - | 本次获得分值 |
| note | string | 否 | "" | 备注 |
| record_type | string | 否 | "manual" | 记录类型 (manual/auto) |

**请求示例**

```json
{
  "behavior_id": 1,
  "points": 3,
  "note": "今天很认真",
  "record_type": "manual"
}
```

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "id": 100,
  "behavior_id": 1,
  "behavior_name": "阅读 30 分钟",
  "behavior_icon": "📚",
  "points": 3,
  "note": "今天很认真",
  "record_type": "manual",
  "created_at": "2026-04-03T20:30:00"
}
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 记录 ID |
| behavior_id | integer | 行为 ID |
| behavior_name | string | 行为名称 |
| behavior_icon | string | 行为图标 |
| points | float | 获得分值 |
| note | string | 备注 |
| record_type | string | 记录类型 |
| created_at | datetime | 创建时间 |

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 404 | 孩子不存在 / 行为不存在 |

---

#### 获取打卡记录

获取指定孩子的打卡记录列表。

**请求**

```
GET /api/children/{child_id}/records
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| child_id | integer | 孩子 ID |

**查询参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| date_from | string | 否 | - | 开始日期 (YYYY-MM-DD) |
| date_to | string | 否 | - | 结束日期 (YYYY-MM-DD) |
| limit | integer | 否 | 50 | 返回数量限制 |

**请求示例**

```
GET /api/children/1/records?date_from=2026-04-01&date_to=2026-04-03&limit=20
```

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
[
  {
    "id": 100,
    "behavior_id": 1,
    "behavior_name": "阅读 30 分钟",
    "behavior_icon": "📚",
    "points": 3,
    "note": "今天很认真",
    "record_type": "manual",
    "created_at": "2026-04-03T20:30:00"
  },
  {
    "id": 99,
    "behavior_id": 6,
    "behavior_name": "完成作业",
    "behavior_icon": "✏️",
    "points": 5,
    "note": "",
    "record_type": "manual",
    "created_at": "2026-04-03T19:00:00"
  }
]
```

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 404 | 孩子不存在或不属于当前用户 |

---

### 积分统计接口

所有积分统计接口需要 **Bearer Token 认证**。

#### 获取积分统计

获取指定孩子的积分统计数据。

**请求**

```
GET /api/children/{child_id}/scores
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| child_id | integer | 孩子 ID |

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "today_points": 8,
  "total_points": 256.5,
  "streak_days": 15,
  "behavior_stats": [
    {"category": "学习", "points": 150.0},
    {"category": "运动", "points": 80.5},
    {"category": "生活习惯", "points": 26.0}
  ]
}
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| today_points | float | 今日获得积分 |
| total_points | float | 累计总积分 |
| streak_days | integer | 连续打卡天数 |
| behavior_stats | array | 各分类积分统计 |
| behavior_stats[].category | string | 分类名称 |
| behavior_stats[].points | float | 该分类积分 |

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 404 | 孩子不存在或不属于当前用户 |

---

#### 获取积分趋势图

获取指定孩子的积分趋势数据。

**请求**

```
GET /api/children/{child_id}/scores/chart
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| child_id | integer | 孩子 ID |

**查询参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| days | integer | 否 | 30 | 天数 |

**请求示例**

```
GET /api/children/1/scores/chart?days=7
```

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "labels": ["2026-03-28", "2026-03-29", "2026-03-30", "2026-03-31", "2026-04-01", "2026-04-02", "2026-04-03"],
  "values": [5.0, 8.0, 0, 12.0, 7.5, 10.0, 8.0]
}
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| labels | array | 日期标签列表 |
| values | array | 每日积分列表 |

---

### 等级接口

所有等级接口需要 **Bearer Token 认证**。

#### 获取孩子等级信息

获取指定孩子的等级和升级进度信息。

**请求**

```
GET /api/children/{child_id}/level
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| child_id | integer | 孩子 ID |

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "current_level": {
    "level": 3,
    "name": "闪亮星",
    "name_en": "Shining Star",
    "icon": "💫",
    "planet": "流星星",
    "color": "#FF69B4",
    "min_points": 150
  },
  "next_level": {
    "level": 4,
    "name": "智慧星",
    "name_en": "Smart Star",
    "icon": "🧠",
    "planet": "知识星",
    "color": "#4169E1",
    "min_points": 300
  },
  "total_points": 256.5,
  "progress_percent": 71.0,
  "points_to_next": 43.5,
  "leveled_up_today": false
}
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| current_level | object | 当前等级信息 |
| current_level.level | integer | 等级 |
| current_level.name | string | 等级中文名 |
| current_level.name_en | string | 等级英文名 |
| current_level.icon | string | 等级图标 |
| current_level.planet | string | 代表星球 |
| current_level.color | string | 代表颜色 |
| current_level.min_points | float | 最低积分要求 |
| next_level | object | 下一等级信息（null 表示已满级） |
| total_points | float | 当前总积分 |
| progress_percent | float | 升级进度百分比 |
| points_to_next | float | 距离下一级所需积分 |
| leveled_up_today | boolean | 今天是否升级 |

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 404 | 孩子不存在或不属于当前用户 |

---

### 用户接口

#### 修改密码

修改当前用户的密码。

**请求**

```
POST /api/user/change-password
```

**请求参数 (Body)**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 当前密码 |
| new_password | string | 是 | 新密码 |

**请求示例**

```json
{
  "old_password": "oldpass123",
  "new_password": "newpass456"
}
```

**请求头**

```
Authorization: Bearer <token>
```

**响应示例**

```json
{
  "message": "密码修改成功"
}
```

**错误响应**

| 状态码 | 说明 |
|--------|------|
| 400 | 当前密码错误 |
| 404 | 用户不存在 |

---

## 附录

### 默认行为分类

| 分类 | 说明 |
|------|------|
| 学习 | 阅读、口算、英语、练琴等 |
| 生活 | 早起、整理房间、按时睡觉等 |
| 运动 | 户外运动、跳绳、游泳等 |
| 其他 | 帮忙做事、不当行为等 |

### 等级体系

| 等级 | 名称 | 最低积分 | 图标 |
|------|------|----------|------|
| 1 | 萌芽宝宝 | 0 | 🌱 |
| 2 | 小小星 | 50 | 🌟 |
| 3 | 闪亮星 | 150 | 💫 |
| 4 | 智慧星 | 300 | 🧠 |
| 5 | 勇敢星 | 500 | ⚡ |
| 6 | 全能星 | 800 | 🏆 |
| 7 | 超级星 | 1200 | 🚀 |
| 8 | 传奇星 | 1800 | 👑 |
| 9 | 至尊星 | 2500 | 💎 |
| 10 | 宇宙星神 | 3500 | 🌌 |

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token 无效或缺失） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

# 远程访问指南

## 公网 IP vs 内网 IP

- **内网 IP** (10.1.1.170): 只能在服务器所在的局域网内访问
- **公网 IP**: 可以从互联网任何地方访问

## 查找公网 IP

运行以下命令查找服务器的公网 IP：

```bash
curl ifconfig.me
# 或
curl ipinfo.io/ip
# 或
curl icanhazip.com
```

## 访问地址

找到公网 IP 后，使用以下地址访问：

```
http://<公网IP>:5173/
```

例如，如果公网 IP 是 `123.45.67.89`，则访问：
```
http://123.45.67.89:5173/
```

## 配置步骤

### 1. 确保 Vite 允许外部访问

`vite.config.js` 中已配置 `host: true`，这允许外部访问。

### 2. 开放防火墙端口

```bash
# 检查防火墙状态
sudo ufw status

# 开放 5173 端口（前端）
sudo ufw allow 5173/tcp

# 开放 5000 端口（后端 API）
sudo ufw allow 5000/tcp

# 如果使用云服务器，还需要在云平台的安全组中开放这些端口
```

### 3. 云服务器安全组配置

如果使用 AWS、阿里云、腾讯云等云服务器，需要在控制台配置安全组：

1. 登录云服务器控制台
2. 找到安全组/防火墙规则
3. 添加入站规则：
   - 端口：5173，协议：TCP，来源：0.0.0.0/0
   - 端口：5000，协议：TCP，来源：0.0.0.0/0

### 4. 启动服务器

```bash
# 前端（已启动）
cd /home/ubuntu/infinigen_web/infinigen-web-frontend
npm run dev

# 后端（在另一个终端）
cd /home/ubuntu/infinigen_web
python3 app.py
```

## 访问测试

### 测试前端
```bash
curl http://<公网IP>:5173
```

### 测试后端 API
```bash
curl http://<公网IP>:5000/api/health
```

## 常见问题

### 1. 无法访问（连接超时）
- 检查防火墙是否开放端口
- 检查云服务器安全组配置
- 检查 Vite 配置 `host: true`

### 2. 可以访问但页面空白
- 检查浏览器控制台（F12）的错误
- 检查后端 API 是否可访问
- 检查 CORS 配置

### 3. API 请求失败
- 确保后端服务器已启动
- 检查 `App.jsx` 中的 `API_BASE_URL` 配置
- 如果前端通过公网 IP 访问，后端 API 地址也需要使用公网 IP

## 修改 API 地址

如果前端通过公网 IP 访问，需要修改 `src/App.jsx` 中的 API 地址：

```javascript
// 将这行：
const API_BASE_URL = 'http://localhost:5000/api';

// 改为（使用公网 IP）：
const API_BASE_URL = 'http://<公网IP>:5000/api';
```

或者使用相对路径（如果前后端在同一服务器）：
```javascript
const API_BASE_URL = '/api';  // 需要配置反向代理
```


# 故障排除指南

## 服务器已启动但无法访问网页

### 1. 检查访问地址

从终端输出可以看到两个地址：
- **Local**: http://localhost:5173/ （仅本机访问）
- **Network**: http://10.1.1.170:5173/ （局域网访问）

**如果你在远程服务器上**，应该使用 Network 地址：
```
http://10.1.1.170:5173/
```

**如果你在本机**，使用 Local 地址：
```
http://localhost:5173/
```

### 2. 检查浏览器控制台

打开浏览器开发者工具（F12），查看 Console 标签页是否有错误信息。

常见错误：
- `Failed to fetch` - 可能是 CORS 问题或后端未启动
- `Cannot find module` - 依赖未正确安装
- `SyntaxError` - 代码语法错误

### 3. 检查后端服务器

前端需要连接后端 API (http://localhost:5000)，确保后端已启动：

```bash
# 在另一个终端窗口
source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen
cd /home/ubuntu/infinigen_web
python3 app.py
```

### 4. 检查防火墙

如果使用 Network 地址无法访问，可能需要开放端口：

```bash
# 检查防火墙状态
sudo ufw status

# 如果需要，开放 5173 端口
sudo ufw allow 5173
```

### 5. 检查代码是否有错误

查看 Vite 终端输出，看是否有编译错误（通常是红色错误信息）。

### 6. 清除缓存重新启动

```bash
# 停止服务器 (Ctrl+C)
# 清除缓存
rm -rf node_modules/.vite
# 重新启动
npm run dev
```

## 快速诊断命令

```bash
# 1. 检查服务器是否响应
curl http://localhost:5173

# 2. 检查端口是否被占用
netstat -tuln | grep 5173

# 3. 检查后端 API 是否可用
curl http://localhost:5000/api/health
```


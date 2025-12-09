# 场景生成时间说明

## 正常情况

**场景生成需要 5-15 分钟是正常的！**

Infinigen 的场景生成是一个复杂的过程，包括：
- 生成房间结构
- 放置家具和装饰
- 优化布局
- 生成材质和纹理
- 设置光照

## 进度提示

程序运行时会显示：
1. 开始生成场景的提示
2. Infinigen 的详细进度日志（实时输出）
3. 场景生成成功的确认

## 如果程序看起来"卡住"了

### 检查方法

1. **查看进程是否在运行**：
   ```bash
   ps aux | grep python | grep generate_indoors
   ```

2. **查看输出文件夹是否有新文件**：
   ```bash
   ls -lht /home/ubuntu/infinigen/outputs/test_workflow/coarse/
   ```

3. **查看系统资源使用**：
   ```bash
   top
   # 或
   htop
   ```

### 正常现象

- ✅ CPU 使用率较高（说明正在计算）
- ✅ 内存使用逐渐增加
- ✅ 输出文件夹中不断有新文件生成
- ✅ 进程状态为 "R" (Running)

### 异常情况

如果出现以下情况，可能是真的卡住了：

- ❌ CPU 使用率为 0%
- ❌ 进程状态为 "S" (Sleeping) 且长时间不变
- ❌ 超过 30 分钟没有任何输出
- ❌ 输出文件夹没有任何新文件

## 加速场景生成

### 方法1: 使用更简单的配置

```bash
python run_agent.py "..." \
    --auto-generate \
    --output-folder ... \
    --gin-configs base disable/no_objects disable/terrain
```

### 方法2: 使用已有场景

如果已有场景文件，可以直接使用，跳过生成步骤：

```bash
python run_agent.py "..." existing_scene.blend --render-image
```

### 方法3: 设置超时

如果担心卡住，可以设置超时：

```bash
python run_agent.py "..." \
    --auto-generate \
    --output-folder ... \
    --generate-timeout 1800  # 30分钟超时
```

## 典型时间线

```
0:00 - 开始生成场景
0:01 - 初始化房间结构
0:02 - 生成地形（如果有）
0:05 - 放置大型家具
0:08 - 放置小型装饰
0:10 - 优化布局
0:12 - 生成材质
0:14 - 完成场景生成
```

**注意**：实际时间取决于场景复杂度和系统性能。

## 监控进度

### 实时查看日志

如果使用 `run_test.sh`，日志会实时显示。

### 查看输出文件

```bash
# 监控输出文件夹
watch -n 5 'ls -lht /home/ubuntu/infinigen/outputs/test_workflow/coarse/ | head -10'
```

### 查看进程

```bash
# 查看进程详情
ps aux | grep generate_indoors
```

## 如果确实卡住了

1. **等待至少 15 分钟**（正常生成时间）

2. **检查错误日志**：
   ```bash
   # 查看是否有错误输出
   tail -f /path/to/log/file
   ```

3. **终止并重试**：
   ```bash
   # 找到进程ID
   ps aux | grep generate_indoors
   # 终止进程
   kill <PID>
   # 重试，使用更简单的配置
   ```

4. **使用已有场景**：
   如果场景生成一直有问题，可以使用已有的场景文件进行测试。

# Infinigen Agent - 使用指南

## 快速开始

### 运行完整测试

```bash
cd /home/ubuntu/infinigen/infinigen_agent
python test_langchain_agent.py
```

这将运行完整的流程测试：
1. ✅ 验证用户输入
2. ✅ 生成家具颜色方案
3. ✅ 生成场景（使用官方推荐配置，完全匹配 hello_room）
4. ✅ 应用颜色到场景
5. ✅ 渲染图片

**预计时间：8-13 分钟**

### 监控测试进度

**方法 1: 实时监控（推荐）**
```bash
cd /home/ubuntu/infinigen/infinigen_agent
python monitor_with_progress.py
```
这会显示实时进度条和当前阶段。

**方法 2: 快速检查状态**
```bash
cd /home/ubuntu/infinigen
python infinigen_agent/check_current_test.py
```
这会显示当前测试的完成阶段。

## 配置说明

当前使用**官方推荐配置**（完全匹配 HelloRoom.md）：

- **基础配置**: `base_indoors.gin` (自动加载)
- **快速配置**: `fast_solve.gin` (迭代次数: 50/20/3)
- **单房间配置**: `singleroom.gin` (限制为 1 个房间)
- **参数覆盖**: `terrain_enabled=False` (禁用地形)

这与官方文档中的命令完全一致：
```bash
python -m infinigen_examples.generate_indoors \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False
```

## 输出文件

测试完成后，输出文件位于：
```
/home/ubuntu/infinigen/outputs/test_langchain_<timestamp>/
├── scene.blend          # 场景文件
├── scene_colored.blend   # 应用颜色后的场景文件
├── pipeline_coarse.csv   # 生成进度记录
└── frames/               # 渲染图片
    └── Image/
        └── camera_0/
            └── Image_0_0_0001_0.png
```

## 查看结果

### 查看渲染图片
```bash
# 找到最新的测试目录
cd /home/ubuntu/infinigen/outputs
ls -lt test_langchain_*/frames/Image/camera_0/Image_*.png | head -1
```

### 在 Blender 中打开场景
```bash
python -m infinigen.launch_blender outputs/test_langchain_<timestamp>/scene_colored.blend
```

## 相关文档

- `CONFIG_VERIFICATION.md` - 配置验证和继承关系说明
- `OFFICIAL_HELLO_ROOM.md` - 官方 Hello Room 配置说明

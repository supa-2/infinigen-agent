# 快速开始指南

## 常用命令速查

**重要提示**: 所有命令都需要在 `infinigen_agent` 目录下运行！

```bash
cd /home/ubuntu/infinigen/infinigen_agent
```

### 0. 自动生成场景（从零开始，推荐）

```bash
# 最简单的方式：自动生成场景并渲染图片
python3 run_agent.py "生成一个北欧风的卧室" \
    --auto-generate \
    --output-folder outputs/my_room \
    --render-image

# 指定随机种子（相同种子生成相同场景）
python run_agent.py "生成一个现代简约风格的客厅" \
    --auto-generate \
    --output-folder outputs/modern_room \
    --seed 42 \
    --render-image \
    --resolution 1920 1080

# 完整流程：生成场景 + 应用颜色 + 渲染图片 + 渲染视频
python run_agent.py "生成一个北欧风的卧室" \
    --auto-generate \
    --output-folder outputs/nordic_bedroom \
    --render-image \
    --render-video \
    --video-frames 60 \
    --video-fps 24
```

### 1. 使用已有场景文件（只应用颜色）

```bash
# 确保在 infinigen_agent 目录下
cd /home/ubuntu/infinigen/infinigen_agent

# 生成带颜色的场景
python3 run_agent.py "生成一个北欧风的卧室" ../outputs/hello_room/coarse/scene.blend

# 指定输出文件
python run_agent.py "生成一个现代简约风格的客厅" scene.blend -o output_colored.blend
```

### 2. 生成场景并渲染图片

```bash
# 低分辨率快速测试
python run_agent.py "生成一个北欧风的卧室" scene.blend \
    --render-image \
    --resolution 640 480

# 高清渲染
python run_agent.py "生成一个北欧风的卧室" scene.blend \
    --render-image \
    --resolution 1920 1080
```

### 3. 生成场景并渲染视频

```bash
# 短视频（10帧，快速测试）
python run_agent.py "生成一个北欧风的卧室" scene.blend \
    --render-video \
    --video-frames 10 \
    --video-fps 24

# 完整视频（60帧）
python run_agent.py "生成一个北欧风的卧室" scene.blend \
    --render-video \
    --video-frames 60 \
    --video-fps 30 \
    --resolution 1280 720
```

### 4. 同时渲染图片和视频

```bash
python run_agent.py "生成一个北欧风的卧室" scene.blend \
    --render-image \
    --render-video \
    --video-frames 60 \
    --video-fps 24 \
    --resolution 1920 1080
```

### 5. 测试脚本

```bash
# 运行所有测试
./test_all.sh

# 渲染测试
./run_render_test.sh

# 检查渲染状态
./check_render_status.sh

# Python 测试
python test_vllm.py              # vLLM 连接
python test_color_parser.py      # 颜色解析
python test_render_simple.py     # 简单渲染
python quick_render_test.py      # 快速渲染
```

## 工作流程示例

### 完整流程：从生成到渲染

```bash
# 步骤1: 生成场景（如果还没有）
# （使用 Infinigen 生成场景，这里假设场景已存在）

# 步骤2: 应用颜色并渲染
python run_agent.py "生成一个北欧风的卧室" \
    ../outputs/hello_room/coarse/scene.blend \
    --render-image \
    --render-video \
    --video-frames 60 \
    --video-fps 24 \
    --resolution 1920 1080

# 步骤3: 检查输出
ls -lh ../outputs/hello_room/coarse/
# 应该看到：
# - scene_colored.blend      # 带颜色的场景
# - rendered_image.png       # 渲染的图片
# - video_output/            # 视频输出文件夹
#   ├── frames/             # 渲染的帧
#   └── output.mp4          # 合成的视频
```

## 常见问题

### Q: 渲染很慢怎么办？
A: 使用较低分辨率进行测试：
```bash
--resolution 640 480  # 快速测试
--resolution 1280 720 # 中等质量
--resolution 1920 1080 # 高清（较慢）
```

### Q: 视频渲染失败？
A: 检查是否安装了 ffmpeg：
```bash
ffmpeg -version
# 如果未安装：
sudo apt install ffmpeg
```

### Q: 如何检查渲染进度？
A: 使用状态检查脚本：
```bash
./check_render_status.sh
```

### Q: 场景文件在哪里？
A: Infinigen 生成的场景通常在：
```
../outputs/hello_room/coarse/scene.blend
```

## 性能建议

1. **测试时使用低分辨率**：`--resolution 640 480`
2. **视频测试使用少量帧**：`--video-frames 10`
3. **生产环境使用合适的分辨率**：`--resolution 1920 1080`
4. **视频帧率**：24 fps 通常足够，30 fps 更流畅但更慢

## 输出文件说明

```
outputs/
├── scene_colored.blend          # 带颜色的场景文件
├── rendered_image.png            # 渲染的图片（如果启用）
└── video_output/                 # 视频输出文件夹（如果启用）
    ├── frames/                   # 渲染的帧
    │   ├── frame_0001.png
    │   ├── frame_0002.png
    │   └── ...
    └── output.mp4                # 合成的视频
```

# 渲染功能说明

Infinigen Agent 现在支持渲染场景图片和视频！

## 功能

### 1. 渲染图片
- 渲染单张场景图片
- 支持自定义分辨率
- 输出 PNG 格式

### 2. 渲染视频
- 渲染多帧图片序列
- 使用 ffmpeg 合成视频
- 支持自定义帧数和帧率

## 使用方法

### 方法1: 命令行（推荐）

#### 只渲染图片
```bash
python run_agent.py "生成一个nordic的bedroom" scene.blend \
    --render-image \
    --resolution 1920 1080
```

#### 只渲染视频
```bash
python run_agent.py "生成一个nordic的bedroom" scene.blend \
    --render-video \
    --video-frames 60 \
    --video-fps 24
```

#### 同时渲染图片和视频
```bash
python run_agent.py "生成一个nordic的bedroom" scene.blend \
    --render-image \
    --render-video \
    --video-frames 120 \
    --video-fps 30 \
    --resolution 1920 1080
```

### 方法2: Python 代码

```python
from src.agent import InfinigenAgent

agent = InfinigenAgent()

# 处理请求并渲染图片
results = agent.process_request_with_render(
    user_request="生成一个nordic的bedroom",
    scene_path="scene.blend",
    render_image=True,
    render_video=True,
    video_frames=60,
    video_fps=24,
    resolution=(1920, 1080)
)

print(f"场景: {results['colored_scene']}")
print(f"图片: {results['image']}")
print(f"视频: {results['video']}")
```

### 方法3: 分步使用

```python
from src.scene_renderer import SceneRenderer

# 渲染图片
renderer = SceneRenderer("scene.blend")
renderer.render_image("output.png", resolution=(1920, 1080))

# 渲染视频
renderer.render_and_create_video(
    output_folder="video_output",
    num_frames=60,
    fps=24
)
```

## 参数说明

- `--render-image`: 渲染图片
- `--render-video`: 渲染视频
- `--video-frames`: 视频帧数（默认60）
- `--video-fps`: 视频帧率（默认24）
- `--resolution WIDTH HEIGHT`: 分辨率，如 `1920 1080`

## 依赖

### 必需
- Blender (已通过 bpy 集成)
- Infinigen 渲染模块

### 可选（视频功能）
- ffmpeg: 用于合成视频
  ```bash
  sudo apt install ffmpeg
  ```

## 输出文件结构

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

## 注意事项

1. **渲染时间**: 
   - 图片渲染通常需要几秒到几分钟
   - 视频渲染时间 = 单帧时间 × 帧数

2. **分辨率**: 
   - 高分辨率会显著增加渲染时间
   - 建议测试时使用较低分辨率（如 640x480）

3. **相机**: 
   - 如果场景中没有相机，会自动创建默认相机
   - 默认相机从上方俯视场景

4. **ffmpeg**: 
   - 如果未安装 ffmpeg，视频功能将不可用
   - 图片渲染不受影响

## 示例

### 快速测试
```bash
# 生成场景并渲染一张低分辨率图片
python run_agent.py "生成一个nordic的bedroom" scene.blend \
    --render-image \
    --resolution 640 480
```

### 高质量输出
```bash
# 生成场景、渲染高清图片和视频
python run_agent.py "生成一个nordic的bedroom" scene.blend \
    --render-image \
    --render-video \
    --video-frames 120 \
    --video-fps 30 \
    --resolution 1920 1080
```


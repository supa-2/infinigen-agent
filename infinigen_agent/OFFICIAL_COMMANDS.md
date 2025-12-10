# 官方推荐命令

根据 [HelloRoom.md](../docs/HelloRoom.md) 文档，以下是官方推荐的各种房间类型的命令：

## 快速测试命令（推荐）

### Diningroom（餐厅）- 最快，~8分钟
```bash
cd /home/ubuntu/infinigen
python -m infinigen_examples.generate_indoors \
  --seed 0 \
  --task coarse \
  --output_folder outputs/test_official_diningroom \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False restrict_solving.restrict_parent_rooms=\[\"DiningRoom\"\]
```

### LivingRoom（客厅）- ~11分钟
```bash
cd /home/ubuntu/infinigen
python -m infinigen_examples.generate_indoors \
  --seed 0 \
  --task coarse \
  --output_folder outputs/test_official_livingroom \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False restrict_solving.restrict_parent_rooms=\[\"LivingRoom\"\]
```

### Bedroom（卧室）- ~10分钟
```bash
cd /home/ubuntu/infinigen
python -m infinigen_examples.generate_indoors \
  --seed 0 \
  --task coarse \
  --output_folder outputs/test_official_bedroom \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False restrict_solving.restrict_parent_rooms=\[\"Bedroom\"\]
```

### Kitchen（厨房）- ~10分钟
```bash
cd /home/ubuntu/infinigen
python -m infinigen_examples.generate_indoors \
  --seed 0 \
  --task coarse \
  --output_folder outputs/test_official_kitchen \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False restrict_solving.restrict_parent_rooms=\[\"Kitchen\"\]
```

### Bathroom（浴室）- ~13分钟
```bash
cd /home/ubuntu/infinigen
python -m infinigen_examples.generate_indoors \
  --seed 0 \
  --task coarse \
  --output_folder outputs/test_official_bathroom \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False restrict_solving.restrict_parent_rooms=\[\"Bathroom\"\]
```

## 最简单的测试（不限制房间类型）

```bash
cd /home/ubuntu/infinigen
python -m infinigen_examples.generate_indoors \
  --seed 0 \
  --task coarse \
  --output_folder outputs/test_official_simple \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False
```

这会随机生成一个单房间场景，预计时间：**8-13 分钟**

## 使用测试脚本

也可以使用我们提供的测试脚本：

```bash
cd /home/ubuntu/infinigen/infinigen_agent
./test_official_command.sh
```

## 监控进度

在另一个终端运行：
```bash
cd /home/ubuntu/infinigen/infinigen_agent
python monitor_with_progress.py
```

## 检查结果

测试完成后，检查输出：
```bash
cd /home/ubuntu/infinigen/outputs
ls -lt test_official_*/
```

查看场景文件：
```bash
python -m infinigen.launch_blender outputs/test_official_*/scene.blend
```

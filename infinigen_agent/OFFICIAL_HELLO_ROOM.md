# 官方 Hello Room 配置说明

## 官方推荐命令

根据 [HelloRoom.md](https://github.com/princeton-vl/infinigen/blob/main/docs/HelloRoom.md) 文档，官方推荐的命令是：

```bash
# Diningroom, single room only, first person view (~8min CPU runtime)
python -m infinigen_examples.generate_indoors \
  --seed 0 \
  --task coarse \
  --output_folder outputs/indoors/coarse \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False restrict_solving.restrict_parent_rooms=\[\"DiningRoom\"\]
```

## 关键配置

### 1. Gin 配置文件 (`-g`)
- `fast_solve.gin`: 减少迭代次数，加快速度
  - `solve_steps_large = 50` (默认 300)
  - `solve_steps_medium = 20` (默认 200)
  - `solve_steps_small = 3` (默认 50)
- `singleroom.gin`: 限制只生成一个房间
  - `restrict_solving.solve_max_rooms=1`

### 2. Gin 参数覆盖 (`-p`)
- `compose_indoors.terrain_enabled=False`: 禁用地形生成，加快速度
- `restrict_solving.restrict_parent_rooms=["DiningRoom"]`: 限制房间类型（可选）

## 我们的实现

我们已经更新代码以完全匹配官方推荐配置：

```python
scene_file = self.scene_generator.generate_scene(
    output_folder=output_folder,
    seed=seed,
    task="coarse",
    gin_configs=['fast_solve', 'singleroom'],  # 官方推荐配置
    gin_overrides=[
        'compose_indoors.terrain_enabled=False'  # 禁用地形，加快速度
    ],
    timeout=timeout
)
```

## 预计时间

根据官方文档：
- Diningroom: ~8 分钟
- Bathroom: ~13 分钟
- Bedroom: ~10 分钟
- Kitchen: ~10 分钟
- LivingRoom: ~11 分钟

## 与之前的区别

| 配置项 | 之前（错误） | 现在（正确） |
|--------|------------|------------|
| Gin 配置 | base_indoors + singleroom | fast_solve + singleroom |
| 迭代次数 | 300/200/50（默认） | 50/20/3（fast_solve） |
| 地形 | 启用 | 禁用（terrain_enabled=False） |
| 预计时间 | 5-10 分钟 | 8-13 分钟 |

## 总结

官方实际上**是使用 fast_solve 的**！这是官方推荐的快速生成配置。我们之前的理解有误，现在已经更正为完全匹配官方推荐的方式。

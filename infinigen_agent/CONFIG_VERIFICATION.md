# 配置验证文档

## 官方命令分析

根据 `generate_indoors.py` 第 518 行：
```python
configs=["base_indoors.gin"] + args.configs,
```

**官方命令：**
```bash
python -m infinigen_examples.generate_indoors \
  --seed 0 --task coarse --output_folder outputs/indoors/coarse \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False
```

**实际加载的配置（按顺序）：**
1. `base_indoors.gin` (自动加载，在 generate_indoors.py 第 518 行)
2. `fast_solve.gin` (通过 `-g` 参数)
3. `singleroom.gin` (通过 `-g` 参数)

## 配置继承关系

### base_indoors.gin (基础配置)
```gin
# overriden in fast_solve.gin if present
compose_indoors.solve_steps_large = 300
compose_indoors.solve_steps_medium = 200
compose_indoors.solve_steps_small = 50
compose_indoors.terrain_enabled = True (默认)
```

### fast_solve.gin (覆盖 base_indoors.gin)
```gin
compose_indoors.solve_steps_large = 50    # 覆盖 300
compose_indoors.solve_steps_medium = 20   # 覆盖 200
compose_indoors.solve_steps_small = 3     # 覆盖 50
compose_indoors.terrain_enabled = False   # 覆盖 True
```

### singleroom.gin
```gin
BlueprintSolidifier.enable_open=False
restrict_solving.solve_max_rooms=1
```

## 最终配置值

使用官方命令后，最终生效的配置：
- `solve_steps_large = 50` (来自 fast_solve.gin，覆盖 base_indoors.gin 的 300)
- `solve_steps_medium = 20` (来自 fast_solve.gin，覆盖 base_indoors.gin 的 200)
- `solve_steps_small = 3` (来自 fast_solve.gin，覆盖 base_indoors.gin 的 50)
- `terrain_enabled = False` (来自 fast_solve.gin + 命令行覆盖)
- `solve_max_rooms = 1` (来自 singleroom.gin)

## 我们的实现

**正确的配置：**
```python
gin_configs=['base_indoors', 'fast_solve', 'singleroom']
gin_overrides=['compose_indoors.terrain_enabled=False']
```

**关键点：**
1. ✅ 必须包含 `base_indoors`（官方会自动加载）
2. ✅ 然后添加 `fast_solve`（覆盖迭代次数）
3. ✅ 然后添加 `singleroom`（限制房间数）
4. ✅ 通过 `gin_overrides` 传递 `terrain_enabled=False`

## 验证

- ✅ 迭代次数：50/20/3（来自 fast_solve.gin）
- ✅ 单房间限制：是（来自 singleroom.gin）
- ✅ 地形禁用：是（来自 fast_solve.gin + override）
- ✅ 配置顺序：base_indoors → fast_solve → singleroom

## 结论

官方推荐配置确实使用：
- **基础配置**: `base_indoors.gin`（自动加载）
- **快速配置**: `fast_solve.gin`（覆盖迭代次数为 50/20/3）
- **单房间配置**: `singleroom.gin`（限制为 1 个房间）
- **参数覆盖**: `terrain_enabled=False`（禁用地形）

我们的实现现在完全匹配官方配置！

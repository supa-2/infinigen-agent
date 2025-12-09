# Infinigen 错误修复报告

## 问题 1: room_walls 阶段错误

### 问题描述

在场景生成的 `room_walls` 阶段出现错误：
```
TypeError: Concrete.generate() got an unexpected keyword argument 'vertical'
```

**错误位置**: `/home/ubuntu/infinigen/infinigen/core/constraints/example_solver/room/decorate.py:229`

## 问题原因

代码在第216-219行定义了 `kwargs`，包含 `vertical=True` 参数：
```python
kwargs = dict(vertical=True, is_ceramic=True, alternating=False, shape="square")
# ...
kwargs = dict(vertical=True, alternating=False, shape=shape)
```

但是：
- `Brick` 类型不接受 `vertical` 参数（第227-228行已处理）
- `Concrete` 类型也不接受 `vertical` 参数（**未处理**）

当 `wall_fn` 是 `Concrete` 类型时，调用 `wall_fn(**kwargs)` 会传递 `vertical=True`，导致错误。

## 修复方案

### 修复 1: 主循环中的处理（第229行）
在调用 `wall_fn(**kwargs)` 之前，检查是否为 `Concrete` 或 `Brick` 类型，如果是则清空 `kwargs`：

```python
# 修复前
if wall_fn.__class__.__name__ == "Brick":
    kwargs = {}

# 修复后
if wall_fn.__class__.__name__ in ("Brick", "Concrete"):
    kwargs = {}
```

### 修复 2: 替代材质处理（第300行）
在 `case _` 分支中，也添加类似的检查：

```python
# 修复前
mat_gen(scale=log_uniform(0.5, 2.0), **kwargs)

# 修复后
mat_kwargs = kwargs.copy()
if mat_gen.__class__.__name__ in ("Brick", "Concrete"):
    mat_kwargs = {k: v for k, v in mat_kwargs.items() if k != "vertical"}
mat_gen(scale=log_uniform(0.5, 2.0), **mat_kwargs)
```

## 修复文件

- `/home/ubuntu/infinigen/infinigen/core/constraints/example_solver/room/decorate.py`
  - 第227行：添加 `Concrete` 类型检查
  - 第299-301行：添加 `Concrete` 和 `Brick` 的 `kwargs` 过滤

## 测试建议

修复后，建议重新运行完整测试：
```bash
cd /home/ubuntu/infinigen/infinigen_agent
python test_langchain_agent.py --full
```

## 预期结果

修复后，场景生成应该能够完成 `room_walls` 阶段，不再出现 `TypeError`。

---

## 问题 2: room_floors 阶段错误

### 问题描述

在场景生成的 `room_floors` 阶段出现错误：
```
TypeError: 'module' object is not callable
```

**错误位置**: `/home/ubuntu/infinigen/infinigen/core/constraints/example_solver/room/decorate.py:331`

### 问题原因

`room_floors` 函数的实现与 `room_walls` 和 `room_ceilings` 不一致：
- `room_walls` 和 `room_ceilings` 都直接调用 `weighted_sample(...)()`
- `room_floors` 分两步：先获取 `gen_class`，再调用 `gen_class()`

当 `weighted_sample` 返回一个模块而不是类时，尝试调用 `gen_class()` 会导致 `TypeError`。

### 修复方案

修改 `room_floors` 函数，使其与 `room_walls` 和 `room_ceilings` 保持一致：

```python
# 修复前
def room_floors(floors, n_floors=3):
    floor_material_gens = []
    for r in floors:
        gen_class = weighted_sample(room_floor_fns[room_type(r.name)])
        floor_material_gens.append(gen_class())

# 修复后
def room_floors(floors, n_floors=3):
    floor_material_gens = list(
        weighted_sample(room_floor_fns[room_type(r.name)])() for r in floors
    )
```

### 修复文件

- `/home/ubuntu/infinigen/infinigen/core/constraints/example_solver/room/decorate.py`
  - 第327-331行：修改 `room_floors` 函数，直接调用 `weighted_sample(...)()`

### 预期结果

修复后，场景生成应该能够完成 `room_floors` 阶段，不再出现 `TypeError`。

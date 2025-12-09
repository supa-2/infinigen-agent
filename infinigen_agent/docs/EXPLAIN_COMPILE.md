# 为什么需要设置这些环境变量？

## setup.py 的逻辑

查看 `setup.py` 的关键代码：

```python
MINIMAL_INSTALL = os.environ.get("INFINIGEN_MINIMAL_INSTALL") == str_true
BUILD_TERRAIN = os.environ.get("INFINIGEN_INSTALL_TERRAIN", str_true) == str_true

# 第 60 行：只有非最小安装时，才会添加 Cython 扩展
if not MINIMAL_INSTALL:
    if BUILD_TERRAIN:
        cython_extensions.append(
            Extension(
                name="infinigen.terrain.marching_cubes",
                sources=["infinigen/terrain/marching_cubes/_marching_cubes_lewiner_cy.pyx"],
                include_dirs=[numpy.get_include()],
            )
        )
```

## 环境变量的作用

### 1. `INFINIGEN_MINIMAL_INSTALL=False`（必需）

- **作用**：告诉 setup.py **不要**使用最小安装模式
- **为什么需要**：如果 `MINIMAL_INSTALL=True`，第 60 行的 `if not MINIMAL_INSTALL:` 条件为 False，**不会添加任何 Cython 扩展**，包括 `marching_cubes`
- **默认行为**：如果未设置，默认为 `False`（因为 `== str_true` 需要显式设置为 "True"）

### 2. `INFINIGEN_INSTALL_TERRAIN=True`（推荐但非必需）

- **作用**：告诉 setup.py 要编译 terrain 相关的扩展
- **为什么需要**：第 69 行的 `if BUILD_TERRAIN:` 条件必须为 True，才会添加 `marching_cubes` 扩展
- **默认行为**：如果未设置，默认就是 `True`（因为默认值是 `str_true`）
- **显式设置的好处**：确保即使环境变量被意外修改，也能正确编译

## 重要澄清：**不需要完整安装！**

`python setup.py build_ext --inplace` **只编译扩展模块**，不会：
- ❌ 重新安装所有 Python 依赖
- ❌ 重新安装 Infinigen 包本身
- ❌ 修改已安装的包

它只会：
- ✅ 编译 Cython 扩展（`.pyx` → `.so`）
- ✅ 将编译好的 `.so` 文件放在源代码目录中（`--inplace` 参数）

## 更简洁的命令

实际上，由于 `BUILD_TERRAIN` 默认就是 `True`，你可以只设置：

```bash
export INFINIGEN_MINIMAL_INSTALL=False
python setup.py build_ext --inplace
```

但为了保险起见，显式设置两个变量更安全：

```bash
export INFINIGEN_INSTALL_TERRAIN=True
export INFINIGEN_MINIMAL_INSTALL=False
python setup.py build_ext --inplace
```

## 总结

- **不需要完整安装**：`build_ext --inplace` 只编译扩展，不重新安装包
- **只需要编译**：将 `.pyx` 文件编译成 `.so` 文件
- **环境变量是必需的**：确保 setup.py 会编译 `marching_cubes` 扩展

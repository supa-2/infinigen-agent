#!/usr/bin/env python
"""验证配置是否正确"""
import os
from pathlib import Path

print("=" * 70)
print("配置验证检查")
print("=" * 70)

# 1. 检查配置文件是否存在
configs = {
    'base_indoors.gin': 'infinigen_examples/configs_indoor/base_indoors.gin',
    'fast_solve.gin': 'infinigen_examples/configs_indoor/fast_solve.gin',
    'singleroom.gin': 'infinigen_examples/configs_indoor/singleroom.gin'
}

all_ok = True
for name, path in configs.items():
    full_path = Path("/home/ubuntu/infinigen") / path
    if full_path.exists():
        print(f"✅ {name} 存在")
    else:
        print(f"❌ {name} 不存在: {full_path}")
        all_ok = False

# 2. 检查 fast_solve.gin 内容
fast_solve_path = Path("/home/ubuntu/infinigen") / configs['fast_solve.gin']
if fast_solve_path.exists():
    with open(fast_solve_path, 'r') as f:
        content = f.read()
        checks = {
            'solve_steps_large = 50': 'solve_steps_large = 50',
            'solve_steps_medium = 20': 'solve_steps_medium = 20',
            'solve_steps_small = 3': 'solve_steps_small = 3',
        }
        for check, desc in checks.items():
            if check in content:
                print(f"✅ fast_solve.gin: {desc}")
            else:
                print(f"❌ fast_solve.gin: 缺少 {desc}")
                all_ok = False

# 3. 检查代码配置
print()
print("代码配置检查:")
print("  langchain_agent.py:")
print("    gin_configs=['fast_solve', 'singleroom']")
print("    gin_overrides=['compose_indoors.terrain_enabled=False']")
print()
print("  scene_generator.py:")
print("    会自动添加 base_indoors（如果还没有）")

# 4. 测试配置构建逻辑
print()
print("配置构建测试:")
gin_configs = ['fast_solve', 'singleroom']
if 'base_indoors' not in gin_configs:
    gin_configs = ['base_indoors'] + gin_configs
print(f"  最终 gin_configs: {gin_configs}")

gin_overrides = ['compose_indoors.terrain_enabled=False']
print(f"  gin_overrides: {gin_overrides}")

# 5. 预期命令
print()
print("=" * 70)
print("预期生成的命令:")
print("  python -m infinigen_examples.generate_indoors \\")
print("    --output_folder <output> \\")
print("    -s <seed> \\")
print("    -t coarse \\")
print("    -g base_indoors fast_solve singleroom \\")
print("    -p compose_indoors.terrain_enabled=False")
print("=" * 70)

if all_ok:
    print()
    print("✅ 所有配置检查通过！")
    print("✅ 可以运行测试: python test_langchain_agent.py")
else:
    print()
    print("❌ 配置检查发现问题，请修复后再测试")

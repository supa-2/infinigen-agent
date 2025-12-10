"""
批量生成场景模板池
为各种房间类型和完整房屋预生成场景模板，存入模板池
"""
import sys
from pathlib import Path
import argparse
import logging
from typing import List, Optional
import time

# 添加项目路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from src.template_pool_manager import TemplatePoolManager
from src.scene_generator import SceneGenerator
from src.room_type_detector import ROOM_TYPES

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 主要支持的房间类型（根据官方文档，这些类型有完整的家具约束）
MAIN_ROOM_TYPES = ["Bedroom", "LivingRoom", "Kitchen", "Bathroom", "DiningRoom"]


def generate_room_templates(
    room_type: str,
    num_templates: int = 5,
    pool_manager: Optional[TemplatePoolManager] = None,
    scene_generator: Optional[SceneGenerator] = None,
    pool_root: Optional[str] = None,
    infinigen_root: Optional[str] = None,
    timeout_per_scene: int = 900,  # 15分钟超时
    start_seed: int = 0,
    gin_configs: Optional[List[str]] = None,
    use_ultra_fast: bool = True
) -> List[str]:
    """
    为指定房间类型生成多个模板
    
    Args:
        room_type: 房间类型，如 "Bedroom", "Kitchen" 等
        num_templates: 要生成的模板数量
        pool_manager: 模板池管理器（如果为None，会创建新的）
        scene_generator: 场景生成器（如果为None，会创建新的）
        pool_root: 模板池根目录
        infinigen_root: Infinigen 根目录
        timeout_per_scene: 每个场景生成的超时时间（秒）
        start_seed: 起始种子值
        gin_configs: gin 配置文件列表
        use_ultra_fast: 是否使用超快配置（ultra_fast_solve.gin）
        
    Returns:
        生成的模板ID列表
    """
    if pool_manager is None:
        pool_manager = TemplatePoolManager(pool_root=pool_root)
    
    if scene_generator is None:
        scene_generator = SceneGenerator(infinigen_root=infinigen_root)
    
    # 默认使用超快配置
    if gin_configs is None:
        if use_ultra_fast:
            gin_configs = ['ultra_fast_solve.gin', 'singleroom.gin']
        else:
            gin_configs = ['fast_solve.gin', 'singleroom.gin']
    
    template_ids = []
    
    logger.info(f"=" * 60)
    logger.info(f"开始为房间类型 {room_type} 生成 {num_templates} 个模板")
    logger.info(f"=" * 60)
    
    for i in range(num_templates):
        seed = start_seed + i
        
        logger.info(f"\n生成模板 {i+1}/{num_templates} (seed: {seed})...")
        
        try:
            # 为每个模板创建独立的输出目录
            output_folder = pool_manager.pool_root / "generating" / f"{room_type.lower()}_{i+1:02d}"
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # gin 覆盖：限制为指定房间类型
            gin_overrides = [
                'compose_indoors.terrain_enabled=False',
                f'restrict_solving.restrict_parent_rooms=\\[\\"{room_type}\\"\\]'
            ]
            
            # 生成场景
            scene_file = scene_generator.generate_scene(
                output_folder=str(output_folder),
                seed=str(seed),
                task="coarse",
                gin_configs=gin_configs,
                gin_overrides=gin_overrides,
                timeout=timeout_per_scene,
                auto_rename=False
            )
            
            # 注册模板
            template_id = pool_manager.register_template(
                scene_file=str(scene_file),
                room_type=room_type,
                seed=str(seed),
                description=f"预生成的 {room_type} 模板 #{i+1}"
            )
            
            template_ids.append(template_id)
            logger.info(f"✓ 模板 {i+1} 生成成功: {template_id}")
            
            # 清理临时生成目录（可选，保留模板文件在pool中）
            # 实际上场景文件应该在 pool_root 中，不需要清理
            
        except Exception as e:
            logger.error(f"✗ 模板 {i+1} 生成失败: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    logger.info(f"\n房间类型 {room_type} 的模板生成完成：{len(template_ids)}/{num_templates} 成功")
    return template_ids


def generate_whole_home_templates(
    num_templates: int = 5,
    pool_manager: Optional[TemplatePoolManager] = None,
    scene_generator: Optional[SceneGenerator] = None,
    pool_root: Optional[str] = None,
    infinigen_root: Optional[str] = None,
    timeout_per_scene: int = 1800,  # 完整房屋需要更长时间，30分钟
    start_seed: int = 1000,
    gin_configs: Optional[List[str]] = None,
    use_ultra_fast: bool = True
) -> List[str]:
    """
    生成完整房屋模板
    
    Args:
        num_templates: 要生成的模板数量
        pool_manager: 模板池管理器
        scene_generator: 场景生成器
        pool_root: 模板池根目录
        infinigen_root: Infinigen 根目录
        timeout_per_scene: 每个场景生成的超时时间（秒）
        start_seed: 起始种子值
        gin_configs: gin 配置文件列表
        use_ultra_fast: 是否使用超快配置
        
    Returns:
        生成的模板ID列表
    """
    if pool_manager is None:
        pool_manager = TemplatePoolManager(pool_root=pool_root)
    
    if scene_generator is None:
        scene_generator = SceneGenerator(infinigen_root=infinigen_root)
    
    # 完整房屋使用不同的配置（不需要 singleroom.gin）
    if gin_configs is None:
        if use_ultra_fast:
            gin_configs = ['ultra_fast_solve.gin']
        else:
            gin_configs = ['fast_solve.gin']
    
    template_ids = []
    
    logger.info(f"=" * 60)
    logger.info(f"开始生成 {num_templates} 个完整房屋模板")
    logger.info(f"⚠ 完整房屋生成时间较长（每个约 20-40 分钟），请耐心等待...")
    logger.info(f"=" * 60)
    
    for i in range(num_templates):
        seed = start_seed + i
        
        logger.info(f"\n生成完整房屋模板 {i+1}/{num_templates} (seed: {seed})...")
        
        try:
            # 为每个模板创建独立的输出目录
            output_folder = pool_manager.pool_root / "generating" / f"whole_home_{i+1:02d}"
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # gin 覆盖：不需要限制房间类型（生成完整房屋）
            gin_overrides = [
                'compose_indoors.terrain_enabled=False'
            ]
            
            # 生成场景
            scene_file = scene_generator.generate_scene(
                output_folder=str(output_folder),
                seed=str(seed),
                task="coarse",
                gin_configs=gin_configs,
                gin_overrides=gin_overrides,
                timeout=timeout_per_scene,
                auto_rename=False
            )
            
            # 注册模板
            template_id = pool_manager.register_template(
                scene_file=str(scene_file),
                room_type=None,  # None 表示完整房屋
                seed=str(seed),
                description=f"预生成的完整房屋模板 #{i+1}"
            )
            
            template_ids.append(template_id)
            logger.info(f"✓ 完整房屋模板 {i+1} 生成成功: {template_id}")
            
        except Exception as e:
            logger.error(f"✗ 完整房屋模板 {i+1} 生成失败: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    logger.info(f"\n完整房屋模板生成完成：{len(template_ids)}/{num_templates} 成功")
    return template_ids


def generate_all_templates(
    room_types: Optional[List[str]] = None,
    templates_per_room: int = 5,
    whole_home_count: int = 5,
    pool_root: Optional[str] = None,
    infinigen_root: Optional[str] = None,
    timeout_per_room: int = 900,
    timeout_per_home: int = 1800,
    use_ultra_fast: bool = True
):
    """
    生成所有模板（所有房间类型 + 完整房屋）
    
    Args:
        room_types: 要生成的房间类型列表，None 表示生成所有主要类型
        templates_per_room: 每个房间类型的模板数量
        whole_home_count: 完整房屋模板数量
        pool_root: 模板池根目录
        infinigen_root: Infinigen 根目录
        timeout_per_room: 每个房间场景的超时时间（秒）
        timeout_per_home: 每个完整房屋场景的超时时间（秒）
        use_ultra_fast: 是否使用超快配置
    """
    if room_types is None:
        room_types = MAIN_ROOM_TYPES
    
    pool_manager = TemplatePoolManager(pool_root=pool_root)
    scene_generator = SceneGenerator(infinigen_root=infinigen_root)
    
    total_start_time = time.time()
    
    # 生成所有房间类型模板
    all_template_ids = []
    for room_type in room_types:
        logger.info(f"\n{'='*60}")
        logger.info(f"开始生成 {room_type} 类型的模板")
        logger.info(f"{'='*60}")
        
        template_ids = generate_room_templates(
            room_type=room_type,
            num_templates=templates_per_room,
            pool_manager=pool_manager,
            scene_generator=scene_generator,
            timeout_per_scene=timeout_per_room,
            start_seed=hash(room_type) % 1000,  # 使用房间类型哈希作为起始种子，确保不同房间类型使用不同的种子范围
            use_ultra_fast=use_ultra_fast
        )
        
        all_template_ids.extend(template_ids)
        
        # 显示进度
        stats = pool_manager.get_statistics()
        logger.info(f"\n当前模板池统计:")
        logger.info(f"  总模板数: {stats['total_templates']}")
        logger.info(f"  总大小: {stats['total_size_mb']:.2f} MB")
    
    # 生成完整房屋模板
    if whole_home_count > 0:
        logger.info(f"\n{'='*60}")
        logger.info(f"开始生成完整房屋模板")
        logger.info(f"{'='*60}")
        
        home_template_ids = generate_whole_home_templates(
            num_templates=whole_home_count,
            pool_manager=pool_manager,
            scene_generator=scene_generator,
            timeout_per_scene=timeout_per_home,
            start_seed=1000,
            use_ultra_fast=use_ultra_fast
        )
        
        all_template_ids.extend(home_template_ids)
    
    # 最终统计
    total_time = time.time() - total_start_time
    stats = pool_manager.get_statistics()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✓ 所有模板生成完成！")
    logger.info(f"{'='*60}")
    logger.info(f"总耗时: {total_time / 3600:.2f} 小时 ({total_time / 60:.2f} 分钟)")
    logger.info(f"生成模板数: {len(all_template_ids)}")
    logger.info(f"\n模板池统计:")
    logger.info(f"  总模板数: {stats['total_templates']}")
    logger.info(f"  总大小: {stats['total_size_mb']:.2f} MB")
    logger.info(f"  模板池目录: {stats['pool_root']}")
    logger.info(f"\n按房间类型分布:")
    for room_type, count in stats['by_room_type'].items():
        logger.info(f"  {room_type}: {count} 个模板")
    
    return all_template_ids


def main():
    parser = argparse.ArgumentParser(
        description="批量生成场景模板池",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成所有主要房间类型的模板（每个5个）
  python generate_template_pool.py --all
  
  # 只生成卧室模板（10个）
  python generate_template_pool.py --room-type Bedroom --count 10
  
  # 生成完整房屋模板（3个）
  python generate_template_pool.py --whole-home --count 3
  
  # 生成所有模板（包括完整房屋）
  python generate_template_pool.py --all --whole-home-count 5
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='生成所有主要房间类型的模板'
    )
    
    parser.add_argument(
        '--room-type',
        type=str,
        choices=MAIN_ROOM_TYPES,
        help='要生成的房间类型'
    )
    
    parser.add_argument(
        '--whole-home',
        action='store_true',
        help='生成完整房屋模板'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='每个类型的模板数量（默认: 5）'
    )
    
    parser.add_argument(
        '--whole-home-count',
        type=int,
        default=5,
        help='完整房屋模板数量（默认: 5）'
    )
    
    parser.add_argument(
        '--pool-root',
        type=str,
        default=None,
        help='模板池根目录（默认: infinigen_agent/templates）'
    )
    
    parser.add_argument(
        '--infinigen-root',
        type=str,
        default=None,
        help='Infinigen 根目录（默认: 自动检测）'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=900,
        help='每个房间场景的超时时间（秒，默认: 900 = 15分钟）'
    )
    
    parser.add_argument(
        '--timeout-home',
        type=int,
        default=1800,
        help='每个完整房屋场景的超时时间（秒，默认: 1800 = 30分钟）'
    )
    
    parser.add_argument(
        '--no-ultra-fast',
        action='store_true',
        help='不使用 ultra_fast_solve.gin（使用 fast_solve.gin 代替）'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出当前模板池中的所有模板'
    )
    
    args = parser.parse_args()
    
    # 如果只是列出模板
    if args.list:
        pool_manager = TemplatePoolManager(pool_root=args.pool_root)
        stats = pool_manager.get_statistics()
        templates = pool_manager.list_templates()
        
        print("\n" + "=" * 60)
        print("模板池统计")
        print("=" * 60)
        print(f"总模板数: {stats['total_templates']}")
        print(f"总大小: {stats['total_size_mb']:.2f} MB")
        print(f"模板池目录: {stats['pool_root']}")
        print("\n按房间类型分布:")
        for room_type, count in stats['by_room_type'].items():
            print(f"  {room_type}: {count} 个模板")
        
        print("\n详细列表:")
        for room_type, template_list in templates.items():
            print(f"\n{room_type}:")
            for template in template_list:
                print(f"  - {template.template_id}: {template.scene_file}")
                print(f"    (seed: {template.seed}, 大小: {template.file_size_mb:.2f} MB)")
        return
    
    use_ultra_fast = not args.no_ultra_fast
    
    # 生成模板
    if args.all:
        # 生成所有模板
        generate_all_templates(
            templates_per_room=args.count,
            whole_home_count=args.whole_home_count if args.whole_home else 0,
            pool_root=args.pool_root,
            infinigen_root=args.infinigen_root,
            timeout_per_room=args.timeout,
            timeout_per_home=args.timeout_home,
            use_ultra_fast=use_ultra_fast
        )
    elif args.whole_home:
        # 只生成完整房屋
        generate_whole_home_templates(
            num_templates=args.count,
            pool_root=args.pool_root,
            infinigen_root=args.infinigen_root,
            timeout_per_scene=args.timeout_home,
            use_ultra_fast=use_ultra_fast
        )
    elif args.room_type:
        # 生成指定房间类型
        generate_room_templates(
            room_type=args.room_type,
            num_templates=args.count,
            pool_root=args.pool_root,
            infinigen_root=args.infinigen_root,
            timeout_per_scene=args.timeout,
            use_ultra_fast=use_ultra_fast
        )
    else:
        parser.print_help()
        print("\n错误: 请指定 --all, --room-type 或 --whole-home 之一")


if __name__ == "__main__":
    main()


"""
预生成池管理器
用于管理预生成的场景模板，实现快速场景生成
"""
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class TemplateMetadata:
    """模板元数据"""
    template_id: str
    room_type: Optional[str]  # 房间类型，如 "Bedroom", "Kitchen" 等，None 表示完整房屋
    scene_file: str  # .blend 文件路径
    seed: str  # 使用的种子
    created_at: str  # 创建时间
    file_size_mb: float  # 文件大小（MB）
    description: Optional[str] = None  # 可选描述


class TemplatePoolManager:
    """模板池管理器"""
    
    def __init__(self, pool_root: Optional[str] = None):
        """
        初始化模板池管理器
        
        Args:
            pool_root: 模板池根目录，默认为 infinigen_agent/templates
        """
        if pool_root is None:
            # 默认模板池目录
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            pool_root = project_root / "templates"
        
        self.pool_root = Path(pool_root).resolve()
        self.pool_root.mkdir(parents=True, exist_ok=True)
        
        # 模板元数据文件
        self.metadata_file = self.pool_root / "templates_metadata.json"
        
        # 加载已有模板元数据
        self.templates: Dict[str, TemplateMetadata] = {}
        self._load_metadata()
        
        logger.info(f"模板池管理器初始化，根目录: {self.pool_root}")
        logger.info(f"已加载 {len(self.templates)} 个模板")
    
    def _load_metadata(self):
        """从文件加载模板元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.templates = {
                        tid: TemplateMetadata(**meta)
                        for tid, meta in data.items()
                    }
                logger.info(f"从 {self.metadata_file} 加载了 {len(self.templates)} 个模板")
            except Exception as e:
                logger.warning(f"加载模板元数据失败: {e}，将创建新的元数据文件")
                self.templates = {}
        else:
            self.templates = {}
    
    def _save_metadata(self):
        """保存模板元数据到文件"""
        try:
            data = {
                tid: asdict(meta)
                for tid, meta in self.templates.items()
            }
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"模板元数据已保存到 {self.metadata_file}")
        except Exception as e:
            logger.error(f"保存模板元数据失败: {e}")
    
    def register_template(
        self,
        scene_file: str,
        room_type: Optional[str] = None,
        seed: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """
        注册一个模板到池中
        
        Args:
            scene_file: 场景文件路径（.blend）
            room_type: 房间类型，如 "Bedroom", "Kitchen" 等，None 表示完整房屋
            seed: 使用的种子
            description: 可选描述
            
        Returns:
            模板ID
        """
        scene_path = Path(scene_file)
        if not scene_path.exists():
            raise FileNotFoundError(f"场景文件不存在: {scene_file}")
        
        # 生成模板ID
        if room_type:
            template_id = f"{room_type.lower()}_{len(self.get_templates_by_type(room_type)) + 1:02d}"
        else:
            template_id = f"whole_home_{len(self.get_templates_by_type(None)) + 1:02d}"
        
        # 如果ID已存在，添加时间戳
        if template_id in self.templates:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            template_id = f"{template_id}_{timestamp}"
        
        # 计算文件大小
        file_size_mb = scene_path.stat().st_size / (1024 * 1024)
        
        # 创建元数据
        metadata = TemplateMetadata(
            template_id=template_id,
            room_type=room_type,
            scene_file=str(scene_path.resolve()),
            seed=seed or "unknown",
            created_at=datetime.now().isoformat(),
            file_size_mb=file_size_mb,
            description=description
        )
        
        # 注册模板
        self.templates[template_id] = metadata
        self._save_metadata()
        
        logger.info(f"注册模板: {template_id} ({room_type or 'WholeHome'})")
        return template_id
    
    def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        """获取指定ID的模板"""
        return self.templates.get(template_id)
    
    def get_templates_by_type(self, room_type: Optional[str]) -> List[TemplateMetadata]:
        """
        根据房间类型获取模板列表
        
        Args:
            room_type: 房间类型，如 "Bedroom", "Kitchen" 等，None 表示完整房屋
            
        Returns:
            模板列表
        """
        return [
            template
            for template in self.templates.values()
            if template.room_type == room_type
        ]
    
    def find_best_template(
        self,
        room_type: Optional[str],
        prefer_recent: bool = True
    ) -> Optional[TemplateMetadata]:
        """
        查找最适合的模板
        
        Args:
            room_type: 房间类型，None 表示完整房屋
            prefer_recent: 是否优先选择最近创建的模板
            
        Returns:
            最佳模板，如果未找到则返回 None
        """
        candidates = self.get_templates_by_type(room_type)
        
        if not candidates:
            logger.warning(f"未找到房间类型为 {room_type} 的模板")
            return None
        
        # 如果只有一个候选，直接返回
        if len(candidates) == 1:
            return candidates[0]
        
        # 如果有多个候选，根据偏好选择
        if prefer_recent:
            # 选择最近创建的
            return max(candidates, key=lambda t: t.created_at)
        else:
            # 随机选择一个（但保证可重复性，使用第一个）
            return candidates[0]
    
    def list_templates(self) -> Dict[str, List[TemplateMetadata]]:
        """
        列出所有模板，按房间类型分组
        
        Returns:
            按房间类型分组的模板字典
        """
        grouped = {}
        for template in self.templates.values():
            key = template.room_type or "WholeHome"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(template)
        return grouped
    
    def remove_template(self, template_id: str) -> bool:
        """
        移除一个模板（仅从元数据中移除，不删除文件）
        
        Args:
            template_id: 模板ID
            
        Returns:
            是否成功移除
        """
        if template_id in self.templates:
            del self.templates[template_id]
            self._save_metadata()
            logger.info(f"已移除模板: {template_id}")
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取模板池统计信息"""
        grouped = self.list_templates()
        stats = {
            "total_templates": len(self.templates),
            "by_room_type": {
                room_type: len(templates)
                for room_type, templates in grouped.items()
            },
            "total_size_mb": sum(t.file_size_mb for t in self.templates.values()),
            "pool_root": str(self.pool_root)
        }
        return stats


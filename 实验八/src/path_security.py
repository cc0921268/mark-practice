"""Keep file paths, including resolved symlinks, inside this project."""
from __future__ import annotations

import os
import io
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_path(value: str | os.PathLike[str]) -> Path:
    """Return a resolved project path or reject an outside path before I/O."""
    try:
        path = Path(value).resolve(strict=False)
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise ValueError("无效的本地文件路径") from exc
    if not path.is_relative_to(PROJECT_ROOT):
        raise ValueError(f"禁止访问实验八项目外文件：{path}")
    return path


def project_source(value):
    """Validate path inputs; retain in-memory uploaded streams as streams."""
    if isinstance(value, (str, os.PathLike)):
        return project_path(value)
    if isinstance(value, (io.BytesIO, io.StringIO)):
        return value
    raise ValueError("输入必须是实验八内的文件路径或内存上传数据")


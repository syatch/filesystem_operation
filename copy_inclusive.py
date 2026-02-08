import copy
from enum import IntEnum
from pathlib import Path
import shutil
from typing import Tuple

from flowweave import FlowWeaveResult

from .file_system import FileSystem
from .lock_manager import get_path_lock

class CopyMode(IntEnum):
    FILE = 0
    FOLDER = 1

class CopyInclusiveCfg():
    def __init__(self):
        self.files = []
        self.folders = []

class CopyInclusive(FileSystem):
    def operation_init(self):
        self.include = CopyInclusiveCfg()

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")
        self.message(f"export : {self.export_dir}")

        self.prepare_options()

        for source_dir in self.source_dir:
            for export_dir in self.export_dir:
                self.message(f"Inclusive Copy: {source_dir} -> {export_dir}")
                for file in self.include.files:
                    self.copy_glob_matched(source_dir, export_dir, file, CopyMode.FILE)
                for folder in self.include.folders:
                    self.copy_glob_matched(source_dir, export_dir, folder, CopyMode.FOLDER)

        return result

    def prepare_options(self):
        self.include.files = self.include.files if isinstance(self.include.files, list) else [self.include.files]
        self.include.folders = self.include.folders if isinstance(self.include.folders, list) else [self.include.folders]

    def copy_glob_matched(self, source_dir: str, export_dir: str, pattern: str, mode: CopyMode):
        src_root = Path(source_dir).resolve()
        dst_root = Path(export_dir).resolve()

        lock = get_path_lock(dst_root)
        with lock:
            is_recursive = pattern.startswith("**/")
            is_glob = is_recursive or any(ch in pattern for ch in ["*", "?", "["])

            if not is_glob:
                target = src_root / pattern
                if not target.exists():
                    return

                dst_path = dst_root / pattern
                if mode == CopyMode.FILE and target.is_file():
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, dst_path)
                elif mode == CopyMode.FOLDER and target.is_dir():
                    shutil.copytree(target, dst_path, dirs_exist_ok=True)
                return

            if is_recursive:
                search_pattern = pattern[3:]
                paths = src_root.rglob(search_pattern)
            else:
                paths = src_root.glob(pattern)

            paths = list(paths)
            paths.sort(key=lambda p: len(p.parts))
            for path in paths:
                if (mode == CopyMode.FILE and not path.is_file()) or \
                (mode == CopyMode.FOLDER and not path.is_dir()):
                    continue

                if (mode == CopyMode.FOLDER) and (path.parent in paths):
                    continue

                rel_path = path.relative_to(src_root)
                dst_path = dst_root / rel_path

                if mode == CopyMode.FILE:
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dst_path)
                else:
                    shutil.copytree(path, dst_path, dirs_exist_ok=True)

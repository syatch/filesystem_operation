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

class CopyInclusive(FileSystem):
    def operation_init(self):
        self.include = {}

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")
        self.message(f"export : {self.export_dir}")

        files, folders = self.get_target()
        for source_dir in self.source_dir:
            for export_dir in self.export_dir:
                for file in files:
                    self.copy_glob_matched(source_dir, export_dir, file, CopyMode.FILE)
                for folder in folders:
                    self.copy_glob_matched(source_dir, export_dir, folder, CopyMode.FOLDER)

        return result

    def get_target(self) -> Tuple[list, list]:
        files = self.include.get("files", [])
        folders = self.include.get("folders", [])
        self.message(f"include files : {files}")
        self.message(f"include folders : {folders}")
        return files, folders

    def copy_glob_matched(self, source_dir: str, export_dir: str, pattern: str, mode: CopyMode):
        src_root = Path(source_dir).resolve()
        dst_root = Path(export_dir).resolve()

        lock = get_path_lock(dst_root)
        with lock:
            is_glob = any(ch in pattern for ch in ["*", "?", "["])

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

            adjusted_pattern = pattern
            if pattern.startswith("**/"):
                adjusted_pattern = f"*/*{pattern[3:]}"

            for path in src_root.rglob("*"):
                if (mode == CopyMode.FILE and not path.is_file()) or (mode == CopyMode.FOLDER and not path.is_dir()):
                    continue

                rel_path = path.relative_to(src_root)
                if rel_path.match(pattern) or rel_path.match(adjusted_pattern):
                    dst_path = dst_root / rel_path
                    if mode == CopyMode.FILE:
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(path, dst_path)
                    elif mode == CopyMode.FOLDER:
                        shutil.copytree(path, dst_path, dirs_exist_ok=True)
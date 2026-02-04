import os
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

class CopyExclusive(FileSystem):
    def operation_init(self):
        self.exclude = {}

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")
        self.message(f"export : {self.export_dir}")

        files, folders = self.get_target()
        for source_dir in self.source_dir:
            for export_dir in self.export_dir:
                self.copy_not_matched(source_dir, export_dir, files, folders)

        return result

    def get_target(self) -> Tuple[list, list]:
        files = self.exclude.get("files", [])
        folders = self.exclude.get("folders", [])
        self.message(f"exclude files : {files}")
        self.message(f"exclude folders : {folders}")
        return files, folders

    def copy_not_matched(self, source_dir: str, export_dir: str,
                         exclude_files: list[str], exclude_dirs: list[str]):
        src_root = Path(source_dir).resolve()
        dst_root = Path(export_dir).resolve()
        dst_root.mkdir(parents=True, exist_ok=True)

        lock = get_path_lock(dst_root)
        with lock:
            def is_glob(p: str):
                return any(ch in p for ch in "*?[")

            file_patterns = [(p, is_glob(p)) for p in exclude_files]
            dir_patterns  = [(p, is_glob(p)) for p in exclude_dirs]

            adjusted_dir_patterns = []
            for pat, glob_mode in dir_patterns:
                adjusted_dir_patterns.append((pat, glob_mode))
                if glob_mode and pat.startswith("**/"):
                    adjusted_dir_patterns.append((pat[3:], False))

            def match(rel_path: Path, patterns):
                for pat, glob_mode in patterns:
                    if glob_mode:
                        if rel_path.match(pat):
                            return True
                    else:
                        if rel_path.as_posix() == pat:
                            return True
                return False

            for root, dirs, files in os.walk(src_root):
                root_path = Path(root)
                rel_root = root_path.relative_to(src_root)

                dirs[:] = [
                    d for d in dirs
                    if not match(rel_root / d, adjusted_dir_patterns)
                ]

                target_dir = dst_root / rel_root
                target_dir.mkdir(parents=True, exist_ok=True)

                for f in files:
                    rel_file = rel_root / f
                    if match(rel_file, file_patterns):
                        continue

                    src_file = root_path / f
                    dst_file = target_dir / f
                    shutil.copy2(src_file, dst_file)
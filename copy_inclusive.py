from pathlib import Path
import shutil
from enum import IntEnum

from flowweave import FlowWeaveTask, Result

from .file_system import FileSystem

class CopyMode(IntEnum):
    FILE = 0
    FOLDER = 1

class CopyInclusive(FileSystem):
    def operation_init(self):
        self.include = {}

    def operation(self):
        result = Result.SUCCESS
        self.message(f"source : {self.source_dir}")
        self.message(f"export : {self.export_dir}")

        files, folders = self.get_target()
        for dir in self.export_dir:
            for file in files:
                self.copy_glob_matched(self.source_dir, dir, file, CopyMode.FILE)
            for folder in folders:
                self.copy_glob_matched(self.source_dir, dir, folder, CopyMode.FOLDER)

        return result

    def get_target(self):
        files = self.include.get("files", [])
        folders = self.include.get("folders", [])
        self.message(f"include files : {files}")
        self.message(f"include folders : {folders}")

        return files, folders

    def copy_glob_matched(self, source_dir: str, export_dir: str, pattern: str, mode: CopyMode):
        src_root = Path(source_dir)
        dst_root = Path(export_dir)

        is_glob = any(ch in pattern for ch in ["*", "?", "["])

        # exact match under source_dir
        if not is_glob:
            target = src_root / pattern

            if (mode == CopyMode.FILE) and (target.is_file()):
                dst_path = dst_root / pattern
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, dst_path)

            elif (mode == CopyMode.FOLDER) and (target.is_dir()):
                dst_path = dst_root / pattern
                shutil.copytree(target, dst_path, dirs_exist_ok=True)

            return

        # glob mode
        for path in src_root.rglob("*"):
            if (mode == CopyMode.FILE) and not (path.is_file()):
                continue
            if (mode == CopyMode.FOLDER) and not (path.is_dir()):
                continue

            rel_path = path.relative_to(src_root)

            if rel_path.match(pattern):
                dst_path = dst_root / rel_path

                if mode == CopyMode.FILE:
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dst_path)

                elif mode == CopyMode.FOLDER:
                    shutil.copytree(path, dst_path, dirs_exist_ok=True)

class Task(FlowWeaveTask):
    runner = CopyInclusive

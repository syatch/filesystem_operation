from pathlib import Path
import shutil
from enum import IntEnum

from flowweave import FlowWeaveTask, Result

from .file_system import FileSystem

class CopyMode(IntEnum):
    FILE = 0
    FOLDER = 1

class CopyExclusive(FileSystem):
    def operation_init(self):
        self.exclude = {}

    def operation(self):
        result = Result.SUCCESS
        self.message(f"source : {self.source_dir}")
        self.message(f"export : {self.export_dir}")

        files, folders = self.get_target()
        for dir in self.export_dir:
            self.copy_not_matched(self.source_dir, dir, files, folders)

        return result

    def get_target(self):
        files = self.exclude.get("files", [])
        folders = self.exclude.get("folders", [])
        self.message(f"exclude files : {files}")
        self.message(f"exclude folders : {folders}")

        return files, folders

    def copy_not_matched(self, source_dir: str, export_dir: str,
                        exclude_files: list[str], exclude_dirs: list[str]):
        src_root = Path(source_dir)
        dst_root = Path(export_dir)

        def is_glob(p: str):
            return any(ch in p for ch in ["*", "?", "["])

        file_patterns = [(p, is_glob(p)) for p in exclude_files]
        dir_patterns  = [(p, is_glob(p)) for p in exclude_dirs]

        def match(rel_path: Path, patterns):
            for pat, glob_mode in patterns:
                if glob_mode: # glob
                    if rel_path.match(pat):
                        return True
                else:
                    # exact match
                    if rel_path.parts == (pat,):
                        return True
            return False

        def ignore_func(dir_path, names):
            ignored = []

            for name in names:
                full_path = Path(dir_path) / name
                rel_path = full_path.relative_to(src_root)

                if full_path.is_dir():
                    if match(rel_path, dir_patterns):
                        ignored.append(name)

                elif full_path.is_file():
                    if match(rel_path, file_patterns):
                        ignored.append(name)

            return ignored

        shutil.copytree(src_root, dst_root, dirs_exist_ok=True, ignore=ignore_func)

class Task(FlowWeaveTask):
    runner = CopyExclusive

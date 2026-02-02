from enum import IntEnum
from pathlib import Path
import shutil

from flowweave import FlowWeaveTask, Result

from .file_system import FileSystem

class RemoveMode(IntEnum):
    FILE = 0
    FOLDER = 1

class Remove(FileSystem):
    def operation_init(self):
        self.remove = {}
        self.files = None
        self.folders = None

    def operation(self):
        result = Result.SUCCESS
        self.message(f"source : {self.source_dir}")

        files, folders = self.get_target()
        for file in files:
            self.delete_path_in_source(self.source_dir, file, RemoveMode.FILE)
        for folder in folders:
            self.delete_path_in_source(self.source_dir, folder, RemoveMode.FOLDER)

        return result

    def delete_path_in_source(self, source_dir: str, target_name: str, mode: RemoveMode) -> bool:
        src_root = Path(source_dir).resolve()
        target = (src_root / target_name).resolve()

        if not target.is_relative_to(src_root):
            return False

        if not target.exists():
            return False

        if mode == RemoveMode.FILE and target.is_file():
            target.unlink()
            return True

        if mode == RemoveMode.FOLDER and target.is_dir():
            shutil.rmtree(target)
            return True

        return False

    def get_target(self):
        files = self.remove.get("files", [])
        folders = self.remove.get("folders", [])
        self.message(f"remove files : {files}")
        self.message(f"remove folders : {folders}")

class Task(FlowWeaveTask):
    runner = Remove

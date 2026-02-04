from enum import IntEnum
from pathlib import Path
import shutil
from typing import Tuple

from flowweave import FlowWeaveResult

from .file_system import FileSystem
from .lock_manager import get_path_lock

class RemoveMode(IntEnum):
    FILE = 0
    FOLDER = 1

class Remove(FileSystem):
    def operation_init(self):
        self.remove = {}
        self.files = None
        self.folders = None

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")

        for source_dir in self.source_dir:
            files, folders = self.get_target()
            for file in files:
                self.delete_path_in_source(source_dir, file, RemoveMode.FILE)
            for folder in folders:
                self.delete_path_in_source(source_dir, folder, RemoveMode.FOLDER)

        return result

    def delete_path_in_source(self, source_dir: str, target_name: str, mode: RemoveMode) -> bool:
        src_root = Path(source_dir).resolve()
        target = (src_root / target_name).resolve()

        if not target.is_relative_to(src_root):
            return False

        if not target.exists():
            return False

        lock = get_path_lock(target)
        with lock:
            try:
                if mode == RemoveMode.FILE and target.is_file():
                    target.unlink(missing_ok=True)
                    self.message(f"deleted file: {target}")
                    return True

                if mode == RemoveMode.FOLDER and target.is_dir():
                    shutil.rmtree(target, ignore_errors=False)
                    self.message(f"deleted folder: {target}")
                    return True
            except Exception as e:
                self.message(f"failed to delete {target}: {e}")
                return False

        return False

    def get_target(self) -> Tuple[list, list]:
        files = self.remove.get("files", [])
        folders = self.remove.get("folders", [])
        self.message(f"remove files : {files}")
        self.message(f"remove folders : {folders}")

        return files, folders
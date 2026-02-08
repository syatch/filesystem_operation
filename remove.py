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

class RemoveCfg():
    def __init__(self):
        self.files = []
        self.folders = []

class Remove(FileSystem):
    def operation_init(self):
        self.remove = RemoveCfg()

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")

        self.prepare_options()

        for source_dir in self.source_dir:
            self.message(f"Remove: {source_dir}")
            for file in self.remove.files:
                self.message(f"- file: {file}")
                self.delete_path_in_source(source_dir, file, RemoveMode.FILE)
            for folder in self.remove.folders:
                self.message(f"- folder: {folder}")
                self.delete_path_in_source(source_dir, folder, RemoveMode.FOLDER)

        return result

    def prepare_options(self):
        self.remove.files = self.remove.files if isinstance(self.remove.files, list) else [self.remove.files]
        self.remove.folders = self.remove.folders if isinstance(self.remove.folders, list) else [self.remove.folders]

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
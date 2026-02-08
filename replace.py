import os
from pathlib import Path

from flowweave import FlowWeaveResult

from .file_system import FileSystem
from .lock_manager import get_path_lock

class ReplaceCfg():
    def __init__(self):
        self.files = []
        self.from_str = None
        self.to_str = None

class Replace(FileSystem):
    def operation_init(self):
        self.replace = ReplaceCfg()

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")

        self.prepare_options()

        files = files if isinstance(files, list) else [files]
        for source_dir in self.source_dir:
            self.message(f"Replace: {source_dir}")
            for file in files:
                self.message(f"- file: {file}")
                self.replace_in_file(source_dir, file, self.replace.from_str, self.replace.to_str)

        return result

    def prepare_options(self):
        self.replace.files = self.replace.files if isinstance(self.replace.files, list) else [self.replace.files]

    def replace_in_file(self, source_dir: str, relative_path: str, from_str: str, to_str: str, encoding="utf-8") -> bool:
        src_root = Path(source_dir).resolve()
        target = (src_root / relative_path).resolve()

        if src_root not in target.parents and target != src_root:
            return False

        if not target.exists() or not target.is_file():
            return False

        lock = get_path_lock(target)
        with lock:
            text = target.read_text(encoding=encoding)

            if from_str not in text:
                return False

            tmp_path = target.with_suffix(target.suffix + ".tmp")
            tmp_path.write_text(text.replace(from_str, to_str), encoding=encoding)
            os.replace(tmp_path, target)

        return True
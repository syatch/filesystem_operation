import os
from pathlib import Path

from flowweave import FlowWeaveResult

from .file_system import FileSystem
from .lock_manager import get_path_lock

class Replace(FileSystem):
    def operation_init(self):
        self.replace = None

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")

        files = self.replace.get("files", [])
        files = files if isinstance(files, list) else [files]
        from_str = self.replace.get("from_str")
        to_str = self.replace.get("to_str")

        for source_dir in self.source_dir:
            for file in files:
                self.replace_in_file(source_dir, file, from_str, to_str)
                self.message(f"modify : {file}")

        return result

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
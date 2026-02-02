from pathlib import Path

from flowweave import FlowWeaveTask, Result

from .file_system import FileSystem

class Replace(FileSystem):
    def operation_init(self):
        self.replace = None

    def operation(self):
        result = Result.SUCCESS
        self.message(f"source : {self.source_dir}")

        files = self.replace.get("files", [])
        files = files if isinstance(files, list) else [files]
        for file in files:
            self.replace_in_file(self.source_dir, file, self.replace.get("from_str"), self.replace.get("to_str"))
            self.message(f"modify : {file}")

        return result

    def replace_in_file(self, source_dir: str, relative_path: str, from_str: str, to_str: str, encoding="utf-8") -> bool:
        src_root = Path(source_dir).resolve()
        target = (src_root / relative_path).resolve()

        if src_root not in target.parents and target != src_root:
            return False

        if not target.exists() or not target.is_file():
            return False

        text = target.read_text(encoding=encoding)

        if from_str not in text:
            return False

        text = text.replace(from_str, to_str)
        target.write_text(text, encoding=encoding)
        return True

class Task(FlowWeaveTask):
    runner = Replace

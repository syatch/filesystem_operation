from pathlib import Path
import zipfile

from flowweave import FlowWeaveTask, Result

from .file_system import FileSystem

class Unzip(FileSystem):
    def operation_init(self):
        self.zips = None

    def operation(self):
        result = Result.SUCCESS
        self.message(f"source : {self.source_dir}")
        self.message(f"export : {self.export_dir}")

        if self.zips:
            zips = self.zips if isinstance(self.zips, list) else [self.zips]
        else:
            zips = self.prev_future.get("data", {}).get("zips", [])

        for dir in self.export_dir:
            for zip in zips:
                dst_root = self.unzip_file_from_source(self.source_dir, dir, zip)
                self.message(f"unzip : {dst_root}")

        return result

    def unzip_file_from_source(self, source_dir: str, export_dir: str, zip_name: str) -> Path:
        src_root = Path(source_dir).resolve()
        dst_root = Path(export_dir).resolve()

        zip_path = src_root / zip_name
        if not zip_path.exists():
            raise FileNotFoundError(f"{zip_path} not found")

        dst_root.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dst_root)

        return dst_root

class Task(FlowWeaveTask):
    runner = Unzip

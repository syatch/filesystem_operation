from pathlib import Path
import zipfile

from flowweave import FlowWeaveTask, Result

from .file_system import FileSystem

class Zip(FileSystem):
    def operation_init(self):
        self.level = 9

    def operation(self):
        result = Result.SUCCESS
        self.message(f"source : {self.source_dir}")
        self.message(f"export : {self.export_dir}")

        for dir in self.export_dir:
            zip_path = self.zip_source_dir(self.source_dir, dir)
            self.message(f"zip : {zip_path}")

        return result

    def zip_source_dir(self,
                       source_dir: str,
                       export_dir: str,
                       compression_level: int = 9) -> Path:
        src_path = Path(source_dir).resolve()
        if not src_path.exists() or not src_path.is_dir():
            raise FileNotFoundError(f"{src_path} is not a valid directory")

        if export_dir:
            dst_root = Path(export_dir).resolve()
        else:
            dst_root = src_path.parent

        dst_root.mkdir(parents=True, exist_ok=True)

        zip_path = dst_root / f"{src_path.name}.zip"

        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=compression_level
        ) as zf:
            for file in src_path.rglob("*"):
                if file.is_file():
                    zf.write(file, arcname=file.relative_to(src_path))

        return zip_path

class Task(FlowWeaveTask):
    runner = Zip

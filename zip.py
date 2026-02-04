import os
from pathlib import Path
import tempfile
import zipfile

from flowweave import FlowWeaveResult

from .file_system import FileSystem
from .lock_manager import get_path_lock

class Zip(FileSystem):
    def operation_init(self):
        self.level = 9

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")
        self.message(f"export : {self.export_dir}")

        for source_dir in self.source_dir:
            for export_dir in self.export_dir:
                zip_path = self.zip_source_dir(source_dir, export_dir, self.level)
                self.message(f"zip : {zip_path}")

        return result

    def zip_source_dir(self,
                       source_dir: str,
                       export_dir: str,
                       compression_level: int = 9) -> Path:
        src_path = Path(source_dir).resolve()
        if not src_path.exists() or not src_path.is_dir():
            raise FileNotFoundError(f"{src_path} is not a valid directory")

        dst_root = Path(export_dir).resolve() if export_dir else src_path.parent
        dst_root.mkdir(parents=True, exist_ok=True)

        zip_path = dst_root / f"{src_path.name}.zip"
        lock = get_path_lock(zip_path)

        with lock:
            with tempfile.NamedTemporaryFile(
                dir=dst_root, delete=False, suffix=".zip"
            ) as tmp_file:
                tmp_zip_path = Path(tmp_file.name)

            try:
                with zipfile.ZipFile(
                    tmp_zip_path,
                    mode="w",
                    compression=zipfile.ZIP_DEFLATED,
                    compresslevel=compression_level
                ) as zf:
                    for file in src_path.rglob("*"):
                        if file.is_file():
                            zf.write(file, arcname=file.relative_to(src_path))

                if zip_path.exists():
                    zip_path.unlink()
                os.replace(tmp_zip_path, zip_path)

            finally:
                if tmp_zip_path.exists():
                    tmp_zip_path.unlink(missing_ok=True)

        return zip_path
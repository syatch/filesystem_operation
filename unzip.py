import os
from pathlib import Path
import tempfile
import zipfile

from flowweave import FlowWeaveResult
from .file_system import FileSystem
from .lock_manager import get_path_lock

class UnzipCfg():
    def __init__(self):
        self.zips = None

class Unzip(FileSystem):
    def operation_init(self):
        self.unzip = UnzipCfg()

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")

        if None != self.unzip.zips:
            self.prepare_options()
        else:
            self.unzip.zips = self.prev_future.get("data", {}).get("zips", [])

        for source_dir in self.source_dir:
            for export_dir in self.export_dir:
                for zip in self.unzip.zips:
                    self.message(f"UnZip: {zip} - {source_dir} -> {export_dir}")
                    self.unzip_file_from_source(source_dir, export_dir, zip)

        return result

    def prepare_options(self):
        self.unzip.zips = self.unzip.zips if isinstance(self.unzip.zips, list) else [self.unzip.zips]

    def _safe_extract(self, zf: zipfile.ZipFile, dest: Path):
        dest = dest.resolve()
        for member in zf.infolist():
            member_path = (dest / member.filename).resolve()
            if dest not in member_path.parents and member_path != dest:
                raise RuntimeError(f"Unsafe path in zip: {member.filename}")
            zf.extract(member, dest)

    def unzip_file_from_source(self, source_dir: str, export_dir: str, zip_name: str) -> Path:
        src_root = Path(source_dir).resolve()
        dst_root = Path(export_dir).resolve()
        zip_path = src_root / zip_name

        if not zip_path.exists():
            raise FileNotFoundError(zip_path)

        dst_root.mkdir(parents=True, exist_ok=True)
        lock = get_path_lock(dst_root)
        with lock:
            with tempfile.TemporaryDirectory(dir=dst_root) as tmp_dir:
                tmp_root = Path(tmp_dir)

                with zipfile.ZipFile(zip_path, "r") as zf:
                    self._safe_extract(zf, tmp_root)

                # merge
                for item in tmp_root.rglob("*"):
                    rel = item.relative_to(tmp_root)
                    target = dst_root / rel

                    if item.is_file():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        os.replace(item, target)


        return dst_root
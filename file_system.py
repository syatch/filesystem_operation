
from flowweave import FlowWeaveTaskRunner, Result, TaskData

class FileSystem(FlowWeaveTaskRunner):
    def __init__(self, prev_future):
        self.prev_future = prev_future
        self.return_data = {}

        self.source_dir = None
        self.export_dir = None

        self.operation_init()

    def operation_init(self):
        pass

    def run(self):
        self.get_source_export_dir()

        result = self.operation()

        self.return_data |= {"source_dir" : self.source_dir, "export_dir" : self.export_dir}
        return result, self.return_data

    def operation(self):
        return Result.SUCCESS

    def get_source_export_dir(self):
        if self.prev_future:
            if "pre_source" == self.source_dir:
                self.source_dir = self.prev_future.get("data", {}).get("source_dir")
            elif "pre_export" == self.source_dir:
                self.source_dir = self.prev_future.get("data", {}).get("export_dir")

            if "pre_source" == self.export_dir:
                self.export_dir = self.prev_future.get("data", {}).get("source_dir")
            elif "pre_export" == self.export_dir:
                self.export_dir = self.prev_future.get("data", {}).get("export_dir")

        if not isinstance(self.export_dir, list):
            self.export_dir = [self.export_dir] if self.export_dir else []
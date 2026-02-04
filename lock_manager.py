from threading import Lock
from weakref import WeakValueDictionary

_path_locks: WeakValueDictionary[str, Lock] = WeakValueDictionary()
_lock_create_guard = Lock()

def get_path_lock(path):
    key = str(path.resolve())
    with _lock_create_guard:
        if key not in _path_locks:
            _path_locks[key] = Lock()
        return _path_locks[key]
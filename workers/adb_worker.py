# workers/adb_worker.py
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess

class AdbWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, cmd, timeout=15):
        super().__init__()
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        try:
            r = subprocess.run(
                self.cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            self.finished.emit(r.stdout or r.stderr)
        except Exception as e:
            self.failed.emit(str(e))

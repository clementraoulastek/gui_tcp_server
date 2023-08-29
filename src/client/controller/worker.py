import time
from typing import Optional
from src.client.core.qt_core import QThread, Signal


class Worker(QThread):
    """Tricks to update the GUI with deamon thread

    Args:
        QThread (QThread): Thread
    """

    signal = Signal()

    def __init__(self, parent, polling_interval: Optional[int] = 0.01) -> None:
        super(Worker, self).__init__(parent)
        self._is_running = True
        self.polling_interval = polling_interval

    def run(self) -> None:
        """
        Run the thread
        """
        if not self._is_running:
            self._is_running = True

        while self._is_running:
            self.signal.emit()
            time.sleep(self.polling_interval)

    def stop(self) -> None:
        """
        Stop the thread
        """
        self._is_running = False
        self.terminate()
        self.exit()
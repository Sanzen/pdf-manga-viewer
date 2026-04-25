from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

from app.config import LOADER_YIELD_MS
from app.pdf_document import PdfDocument


class PageLoaderThread(QThread):
    page_ready = pyqtSignal(int, QPixmap)
    loading_progress = pyqtSignal(int, int)
    loading_complete = pyqtSignal()

    def __init__(
        self,
        doc: PdfDocument,
        cache: dict,
        start_page: int,
        target_width: int = 0,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._doc = doc
        self._cache = cache
        self._start = start_page
        self._target_width = target_width
        self._stop_requested = False

    def request_stop(self) -> None:
        self._stop_requested = True

    def run(self) -> None:
        total = self._doc.page_count - self._start
        for n in range(self._start, self._doc.page_count):
            if self._stop_requested:
                return
            pixmap = self._doc.extract_page(n, self._target_width)
            self._cache[n] = pixmap
            self.page_ready.emit(n, pixmap)
            loaded = n - self._start + 1
            self.loading_progress.emit(loaded, total)
            if LOADER_YIELD_MS > 0:
                self.msleep(LOADER_YIELD_MS)
        self.loading_complete.emit()

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from app.pdf_document import PdfDocument


class ReaderWidget(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cache: dict[int, QPixmap] = {}
        self._current_page: int = 0
        self._total_pages: int = 0
        self._zoom_factor: float = 1.0

        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setScaledContents(False)
        self._image_label.setMinimumSize(1, 1)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidget(self._image_label)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._scroll_area)

    @property
    def render_target_width(self) -> int:
        """物理ピクセル解像度でレンダリングする幅を返す（4K上限あり）。"""
        w = self._scroll_area.viewport().width()
        if w <= 0:
            w = 900
        return min(int(w * self.devicePixelRatioF()), 3840)

    @property
    def current_page(self) -> int:
        return self._current_page

    @property
    def total_pages(self) -> int:
        return self._total_pages

    def set_document(self, doc: PdfDocument, cache: dict) -> None:
        self._cache = cache
        self._total_pages = doc.page_count
        self._current_page = 0
        self._zoom_factor = 1.0
        self.display_page(0)

    def display_page(self, n: int) -> None:
        if n not in self._cache:
            return
        pixmap = self._cache[n]
        scaled = self._scale_pixmap(pixmap)
        self._image_label.setPixmap(scaled)
        self._image_label.resize(scaled.size())
        self._current_page = n
        self.page_changed.emit(n)

    def _scale_pixmap(self, pixmap: QPixmap) -> QPixmap:
        dpr = self.devicePixelRatioF()
        vw = self._scroll_area.viewport().width()
        vh = self._scroll_area.viewport().height()
        if vw <= 0 or vh <= 0:
            return pixmap
        phys_w = vw * dpr
        phys_h = vh * dpr
        scale = min(phys_w / pixmap.width(), phys_h / pixmap.height()) * self._zoom_factor
        if scale <= 0:
            return pixmap
        scaled = pixmap.scaled(
            int(pixmap.width() * scale),
            int(pixmap.height() * scale),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        scaled.setDevicePixelRatio(dpr)
        return scaled

    def go_to_page(self, n: int) -> None:
        n = max(0, min(n, self._total_pages - 1))
        self.display_page(n)

    def next_page(self) -> None:
        self.go_to_page(self._current_page + 1)

    def prev_page(self) -> None:
        self.go_to_page(self._current_page - 1)

    def zoom_in(self) -> None:
        self._zoom_factor = min(self._zoom_factor + 0.1, 4.0)
        self.display_page(self._current_page)

    def zoom_out(self) -> None:
        self._zoom_factor = max(self._zoom_factor - 0.1, 0.25)
        self.display_page(self._current_page)

    def reset_zoom(self) -> None:
        self._zoom_factor = 1.0
        self.display_page(self._current_page)

    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            if event.angleDelta().y() < 0:
                self.next_page()
            else:
                self.prev_page()
        event.accept()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.display_page(self._current_page)

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QWidget,
)

from app.config import INITIAL_SYNC_PAGES
from app.page_loader import PageLoaderThread
from app.pdf_document import PdfDocument
from app.reader_widget import ReaderWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cache: dict = {}
        self._doc: PdfDocument | None = None
        self._loader: PageLoaderThread | None = None

        self._reader = ReaderWidget(self)
        self.setCentralWidget(self._reader)
        self._reader.page_changed.connect(self._update_status)

        self._status_label = QLabel("ファイルを開いてください")
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedWidth(200)
        self._progress_bar.setVisible(False)

        status = self.statusBar()
        status.addWidget(self._status_label)
        status.addPermanentWidget(self._progress_bar)

        self._build_menu()
        self.setAcceptDrops(True)
        self.setWindowTitle("MangaReader")
        self.resize(900, 1200)

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("ファイル(&F)")

        open_action = QAction("開く(&O)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("終了(&Q)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("表示(&V)")

        zoom_in_action = QAction("ズームイン(&+)", self)
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(self._reader.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("ズームアウト(&-)", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._reader.zoom_out)
        view_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("ズームリセット(&0)", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self._reader.reset_zoom)
        view_menu.addAction(zoom_reset_action)

    def _on_open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "PDFを開く", "", "PDF Files (*.pdf)"
        )
        if path:
            self.open_pdf(path)

    def open_pdf(self, path: str) -> None:
        self._stop_loader()
        self._cache.clear()

        if self._doc is not None:
            self._doc.close()
            self._doc = None

        try:
            doc = PdfDocument(path)
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"PDFを開けませんでした:\n{e}")
            return

        if doc.page_count == 0:
            QMessageBox.critical(self, "エラー", "このPDFにはページがありません。")
            doc.close()
            return

        self._doc = doc
        target_width = self._reader.render_target_width
        sync_count = min(INITIAL_SYNC_PAGES, doc.page_count)
        for n in range(sync_count):
            self._cache[n] = doc.extract_page(n, target_width)

        self._reader.set_document(doc, self._cache)
        self.setWindowTitle(f"MangaReader — {Path(path).name}")

        start = sync_count
        if start < doc.page_count:
            self._loader = PageLoaderThread(doc, self._cache, start, target_width, self)
            self._loader.page_ready.connect(self._on_page_ready)
            self._loader.loading_progress.connect(self._on_progress)
            self._loader.loading_complete.connect(self._on_loading_complete)
            self._progress_bar.setValue(0)
            self._progress_bar.setVisible(True)
            self._loader.start()

    def _stop_loader(self) -> None:
        if self._loader is not None and self._loader.isRunning():
            self._loader.request_stop()
            self._loader.wait(3000)
        self._loader = None

    def _on_page_ready(self, n: int, pixmap) -> None:
        if n == self._reader.current_page:
            self._reader.display_page(n)

    def _on_progress(self, loaded: int, total: int) -> None:
        if total > 0:
            self._progress_bar.setValue(int(loaded / total * 100))

    def _on_loading_complete(self) -> None:
        self._progress_bar.setVisible(False)

    def _update_status(self, page: int) -> None:
        total = self._reader.total_pages
        self._status_label.setText(f"{page + 1} / {total}")

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (
            Qt.Key.Key_Right,
            Qt.Key.Key_Space,
            Qt.Key.Key_PageDown,
            Qt.Key.Key_Down,
        ):
            self._reader.next_page()
        elif key in (
            Qt.Key.Key_Left,
            Qt.Key.Key_Backspace,
            Qt.Key.Key_PageUp,
            Qt.Key.Key_Up,
        ):
            self._reader.prev_page()
        elif key == Qt.Key.Key_Home:
            self._reader.go_to_page(0)
        elif key == Qt.Key.Key_End:
            self._reader.go_to_page(self._reader.total_pages - 1)
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(u.toLocalFile().lower().endswith(".pdf") for u in urls):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event) -> None:
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if path.lower().endswith(".pdf"):
                self.open_pdf(path)
                break

    def closeEvent(self, event) -> None:
        self._stop_loader()
        if self._doc is not None:
            self._doc.close()
        super().closeEvent(event)

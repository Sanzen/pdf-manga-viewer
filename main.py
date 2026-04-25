import sys

from PyQt6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.pdf_document import is_image_pdf
from app.pdf_reader_detector import detect_and_save_fallback_reader, open_with_fallback


def main() -> None:
    detect_and_save_fallback_reader()

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if not is_image_pdf(path) and open_with_fallback(path):
            sys.exit(0)

    app = QApplication(sys.argv)
    app.setApplicationName("MangaReader")

    window = MainWindow()
    window.show()

    if len(sys.argv) > 1:
        window.open_pdf(sys.argv[1])

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

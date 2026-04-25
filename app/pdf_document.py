import fitz
from PyQt6.QtGui import QImage, QPixmap

from app.config import RENDER_DPI

_TEXT_CHARS_THRESHOLD = 100  # avg chars/page above this → treat as text PDF


def is_image_pdf(path: str) -> bool:
    """Return True if the PDF appears to be image-based (manga/scans)."""
    doc = fitz.open(path)
    sample = min(3, len(doc))
    if sample == 0:
        doc.close()
        return True
    total_chars = sum(len(doc[i].get_text()) for i in range(sample))
    doc.close()
    return (total_chars / sample) <= _TEXT_CHARS_THRESHOLD


class PdfDocument:
    def __init__(self, path: str) -> None:
        self._doc = fitz.open(path)
        self.path = path

    @property
    def page_count(self) -> int:
        return len(self._doc)

    def extract_page(self, page_num: int, target_width: int = 0) -> QPixmap:
        page = self._doc[page_num]
        if target_width > 0:
            scale = target_width / page.rect.width
            matrix = fitz.Matrix(scale, scale)
        else:
            matrix = fitz.Matrix(RENDER_DPI / 72.0, RENDER_DPI / 72.0)
        pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
        image = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888,
        )
        return QPixmap.fromImage(image)

    def close(self) -> None:
        self._doc.close()

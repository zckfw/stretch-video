"""File selection by click or drag and drop."""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFileDialog, QFrame, QLabel, QVBoxLayout


class DropArea(QFrame):
    selected = Signal(Path)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("dropArea")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(210)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        self.title = QLabel("Arraste um vídeo aqui")
        self.title.setObjectName("dropTitle")
        self.title.setAlignment(Qt.AlignCenter)
        self.hint = QLabel("ou clique para selecionar")
        self.hint.setObjectName("dropHint")
        self.hint.setAlignment(Qt.AlignCenter)
        for label in (self.title, self.hint):
            label.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(label)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            name, _ = QFileDialog.getOpenFileName(
                self, "Selecionar vídeo", "", "Vídeos (*.mp4 *.mov *.mkv *.avi *.webm *.m4v);;Todos os arquivos (*)"
            )
            if name:
                self.selected.emit(Path(name))
        super().mousePressEvent(event)

    def dragEnterEvent(self, event) -> None:
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].isLocalFile():
            event.acceptProposedAction()
            self._set_dragging(True)

    def dragLeaveEvent(self, event) -> None:
        self._set_dragging(False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event) -> None:
        self._set_dragging(False)
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].isLocalFile():
            self.selected.emit(Path(urls[0].toLocalFile()))
            event.acceptProposedAction()

    def _set_dragging(self, dragging: bool) -> None:
        self.setProperty("dragging", dragging)
        self.style().unpolish(self)
        self.style().polish(self)

"""Main window for selecting and stretching one video."""

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..backend.processor import VideoProcessor
from .drop_area import DropArea
from .style import STYLE


class StretchWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("stretch-video")
        self.setFixedSize(540, 520)
        self.source: Path | None = None
        self.destination: Path | None = None
        self.processor = VideoProcessor(self)
        self.processor.finished.connect(self._finished)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(38, 34, 38, 34)
        layout.setSpacing(17)

        heading = QLabel("stretch-video")
        heading.setObjectName("heading")
        layout.addWidget(heading)
        intro = QLabel("Estique um vídeo para a resolução que você escolher.")
        intro.setObjectName("muted")
        layout.addWidget(intro)

        self.drop_area = DropArea()
        self.drop_area.selected.connect(self._select_file)
        layout.addWidget(self.drop_area)

        self.details = QWidget()
        details_layout = QVBoxLayout(self.details)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(11)

        self.file_label = QLabel()
        self.file_label.setObjectName("muted")
        self.file_label.setWordWrap(True)
        details_layout.addWidget(self.file_label)

        resolution = QHBoxLayout()
        resolution.setSpacing(10)
        resolution.addWidget(QLabel("Resolução final"))
        self.width_input = QSpinBox()
        self.height_input = QSpinBox()
        for field, value in ((self.width_input, 1920), (self.height_input, 1080)):
            field.setRange(2, 8192)
            field.setSingleStep(2)
            field.setValue(value)
        resolution.addWidget(self.width_input)
        resolution.addWidget(QLabel("×"))
        resolution.addWidget(self.height_input)
        resolution.addStretch()
        details_layout.addLayout(resolution)

        self.save_button = QPushButton("Esticar vídeo")
        self.save_button.setObjectName("primary")
        self.save_button.clicked.connect(self._start)
        details_layout.addWidget(self.save_button)
        self.details.hide()
        layout.addWidget(self.details)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)

        self.status = QLabel("")
        self.status.setObjectName("muted")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.open_folder = QPushButton("Abrir pasta do vídeo")
        self.open_folder.setObjectName("secondary")
        self.open_folder.clicked.connect(self._open_folder)
        self.open_folder.hide()
        layout.addWidget(self.open_folder)
        layout.addStretch()

    def _select_file(self, path: Path) -> None:
        if not path.is_file():
            QMessageBox.warning(self, "Arquivo inválido", "Selecione um arquivo de vídeo válido.")
            return
        self.source = path
        self.file_label.setText(f"Vídeo: {path.name}")
        self.drop_area.title.setText(path.name)
        self.drop_area.hint.setText("Clique ou arraste outro vídeo para trocar")
        self.details.show()
        self.open_folder.hide()
        self.status.clear()

    def _start(self) -> None:
        if self.source is None:
            return
        try:
            self.destination = self.processor.start(
                self.source, self.width_input.value(), self.height_input.value()
            )
        except (RuntimeError, ValueError) as exc:
            QMessageBox.warning(self, "Não foi possível iniciar", str(exc))
            return

        self.save_button.setEnabled(False)
        self.drop_area.setEnabled(False)
        self.progress.show()
        self.status.setText("Processando vídeo...")
        self.open_folder.hide()
    def _finished(self, success: bool, error: str) -> None:
        if self.destination is None:
            return
        self.progress.hide()
        self.save_button.setEnabled(True)
        self.drop_area.setEnabled(True)
        if success:
            self.status.setText(f"Pronto: {self.destination.name}")
            self.open_folder.show()
        else:
            self.status.setText("Não foi possível processar o vídeo.")
            QMessageBox.warning(self, "Erro no FFmpeg", error or "Confira o arquivo e tente novamente.")

    def _open_folder(self) -> None:
        if self.destination is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.destination.parent)))

    def closeEvent(self, event) -> None:
        if self.processor.is_running():
            QMessageBox.information(self, "Vídeo em andamento", "Aguarde o processamento terminar.")
            event.ignore()
            return
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = StretchWindow()
    window.show()
    return app.exec()

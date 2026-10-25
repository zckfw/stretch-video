"""Minimal Qt interface for selecting and stretching one video."""

import sys
from pathlib import Path

from PySide6.QtCore import QProcess, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .video import ffmpeg_arguments, ffmpeg_path, output_path


STYLE = """
QWidget { background: #ffffff; color: #171717; font-family: 'Segoe UI'; font-size: 13px; }
QLabel#heading { font-size: 25px; font-weight: 700; }
QLabel#muted { color: #6b7280; }
QFrame#dropArea { border: 2px dashed #d1d5db; border-radius: 16px; background: #fafafa; }
QFrame#dropArea[dragging="true"] { border-color: #2563eb; background: #eff6ff; }
QLabel#dropTitle { font-size: 17px; font-weight: 600; background: transparent; }
QLabel#dropHint { color: #6b7280; background: transparent; }
QSpinBox { border: 1px solid #d1d5db; border-radius: 8px; padding: 8px; min-width: 92px; }
QPushButton#primary { background: #171717; color: white; border: none; border-radius: 9px; padding: 11px 20px; font-weight: 600; }
QPushButton#primary:hover { background: #374151; }
QPushButton#primary:disabled { background: #9ca3af; }
QPushButton#secondary { border: none; color: #2563eb; font-weight: 600; text-align: left; }
QProgressBar { border: none; border-radius: 3px; background: #e5e7eb; max-height: 6px; }
QProgressBar::chunk { border-radius: 3px; background: #2563eb; }
"""


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


class StretchWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("stretch-video")
        self.setFixedSize(540, 520)
        self.source: Path | None = None
        self.destination: Path | None = None
        self.process: QProcess | None = None

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

        self.save_button = QPushButton("Criar vídeo")
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
            program = ffmpeg_path()
            self.destination = output_path(self.source)
            args = ffmpeg_arguments(
                self.source, self.destination, self.width_input.value(), self.height_input.value()
            )
        except (RuntimeError, ValueError) as exc:
            QMessageBox.warning(self, "Não foi possível iniciar", str(exc))
            return

        self.process = QProcess(self)
        self.process.setProgram(program)
        self.process.setArguments(args)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._process_error)
        self.save_button.setEnabled(False)
        self.drop_area.setEnabled(False)
        self.progress.show()
        self.status.setText("Processando vídeo...")
        self.open_folder.hide()
        self.process.start()

    def _finished(self, exit_code: int, _status) -> None:
        if self.process is None or self.destination is None:
            return
        error = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace").strip()
        self.progress.hide()
        self.save_button.setEnabled(True)
        self.drop_area.setEnabled(True)
        if exit_code == 0 and self.destination.is_file():
            self.status.setText(f"Pronto: {self.destination.name}")
            self.open_folder.show()
        else:
            self.destination.unlink(missing_ok=True)
            self.status.setText("Não foi possível processar o vídeo.")
            QMessageBox.warning(self, "Erro no FFmpeg", error or "Confira o arquivo e tente novamente.")
        self.process.deleteLater()
        self.process = None

    def _process_error(self, _error) -> None:
        if self.process is not None and self.process.state() == QProcess.NotRunning:
            self._finished(-1, None)

    def _open_folder(self) -> None:
        if self.destination is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.destination.parent)))

    def closeEvent(self, event) -> None:
        if self.process is not None and self.process.state() != QProcess.NotRunning:
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

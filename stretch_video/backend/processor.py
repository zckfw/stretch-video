"""Run FFmpeg without blocking the interface."""

from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal

from .video import ffmpeg_arguments, ffmpeg_path, output_path


class VideoProcessor(QObject):
    finished = Signal(bool, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.process: QProcess | None = None
        self.destination: Path | None = None

    def start(self, source: Path, width: int, height: int) -> Path:
        program = ffmpeg_path()
        destination = output_path(source)
        arguments = ffmpeg_arguments(source, destination, width, height)

        self.destination = destination
        self.process = QProcess(self)
        self.process.setProgram(program)
        self.process.setArguments(arguments)
        self.process.finished.connect(self._finish)
        self.process.errorOccurred.connect(self._process_error)
        self.process.start()
        return destination

    def is_running(self) -> bool:
        return self.process is not None and self.process.state() != QProcess.NotRunning

    def _finish(self, exit_code: int, _status) -> None:
        if self.process is None or self.destination is None:
            return
        error = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace").strip()
        success = exit_code == 0 and self.destination.is_file()
        if not success:
            self.destination.unlink(missing_ok=True)
        self.process.deleteLater()
        self.process = None
        self.finished.emit(success, error)

    def _process_error(self, _error) -> None:
        if self.process is not None and self.process.state() == QProcess.NotRunning:
            self._finish(-1, None)

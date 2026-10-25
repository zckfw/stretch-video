"""FFmpeg command and output path handling."""

from pathlib import Path
import shutil


def ffmpeg_path() -> str:
    executable = shutil.which("ffmpeg")
    if executable is None:
        raise RuntimeError("FFmpeg não foi encontrado. Instale o FFmpeg e adicione-o ao PATH.")
    return executable


def output_path(source: Path) -> Path:
    """Choose a new MP4 beside the source without replacing an existing file."""
    base = source.with_name(f"{source.stem}_stretched.mp4")
    if not base.exists():
        return base

    index = 2
    while True:
        candidate = source.with_name(f"{source.stem}_stretched_{index}.mp4")
        if not candidate.exists():
            return candidate
        index += 1


def ffmpeg_arguments(source: Path, destination: Path, width: int, height: int) -> list[str]:
    if not source.is_file():
        raise ValueError("Selecione um arquivo de vídeo válido.")
    if width < 2 or height < 2 or width % 2 or height % 2:
        raise ValueError("A largura e a altura devem ser números pares maiores que zero.")

    return [
        "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
        "-i", str(source),
        "-map", "0:v:0", "-map", "0:a?",
        "-vf", f"scale={width}:{height}:flags=lanczos,setsar=1",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(destination),
    ]

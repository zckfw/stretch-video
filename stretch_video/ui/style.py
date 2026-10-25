"""Styles for the desktop interface."""

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

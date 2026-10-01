from __future__ import annotations

from PyQt6.QtWidgets import QApplication, QWidget


def get_corner_positions(widget: QWidget, margin: int) -> dict[str, tuple[int, int]]:
    screen = widget.screen() or QApplication.primaryScreen()
    if not screen:
        return {}
    geo = screen.availableGeometry()
    w, h = widget.width(), widget.height()
    return {
        "top-left": (geo.left() + margin, geo.top() + margin),
        "top-right": (geo.right() - w - margin, geo.top() + margin),
        "bottom-left": (geo.left() + margin, geo.bottom() - h - margin),
        "bottom-right": (geo.right() - w - margin, geo.bottom() - h - margin),
    }


def get_nearest_corner(widget: QWidget, margin: int) -> str:
    positions = get_corner_positions(widget, margin)
    if not positions:
        return "bottom-right"
    cx = widget.x() + widget.width() / 2
    cy = widget.y() + widget.height() / 2
    nearest = "bottom-right"
    best = float("inf")
    for name, (x, y) in positions.items():
        dx = cx - (x + widget.width() / 2)
        dy = cy - (y + widget.height() / 2)
        dist = dx * dx + dy * dy
        if dist < best:
            best = dist
            nearest = name
    return nearest


def snap_widget_to_corner(
    widget: QWidget,
    margin: int,
    corner: str | None = None,
) -> str:
    positions = get_corner_positions(widget, margin)
    if not positions:
        return "bottom-right"
    target = corner or get_nearest_corner(widget, margin)
    pos = positions.get(target, positions.get("bottom-right"))
    if pos:
        widget.move(pos[0], pos[1])
    return target

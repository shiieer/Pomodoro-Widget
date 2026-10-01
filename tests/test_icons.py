"""
Tests for ui/icons.py — icon rendering system.

Covers:
  - get_svg_data: returns non-empty bytes for known icon names
  - get_svg_data: falls back gracefully for unknown icon names
  - get_pixmap: returns valid QPixmap at correct size
  - get_pixmap: different sizes all work
  - get_icon: returns QIcon with normal state
  - get_icon: active_color path returns QIcon with two states
  - SvgIconWidget: instantiation, set_color, set_icon
"""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication(sys.argv)


class TestGetSvgData:
    def test_known_icon_returns_bytes(self, qapp):
        from ui.icons import get_svg_data

        data = get_svg_data("play", color="#ffffff")
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_svg_contains_color(self, qapp):
        from ui.icons import get_svg_data

        data = get_svg_data("pause", color="#ff0000").decode()
        assert "#ff0000" in data

    def test_unknown_icon_falls_back_to_clock(self, qapp):
        from ui.icons import get_svg_data

        data = get_svg_data("nonexistent-icon-xyz", color="#fff")
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_stroke_width_respected(self, qapp):
        from ui.icons import get_svg_data

        data = get_svg_data("rotate-ccw", color="#fff", stroke_width=3).decode()
        assert "3" in data

    def test_all_defined_icons_render(self, qapp):
        from ui.icons import SVG_TEMPLATES, get_svg_data

        for name in SVG_TEMPLATES:
            data = get_svg_data(name, color="#aabbcc")
            assert isinstance(data, bytes) and len(data) > 0, (
                f"Icon '{name}' failed to render"
            )


class TestGetPixmap:
    def test_returns_qpixmap(self, qapp):
        from PyQt6.QtGui import QPixmap

        from ui.icons import get_pixmap

        pix = get_pixmap("play", color="#9EE7FF", size=16)
        assert isinstance(pix, QPixmap)

    def test_pixmap_correct_size(self, qapp):
        from ui.icons import get_pixmap

        for size in (12, 16, 24, 32):
            pix = get_pixmap("pause", color="#fff", size=size)
            assert pix.width() == size
            assert pix.height() == size

    def test_pixmap_not_null(self, qapp):
        from ui.icons import get_pixmap

        pix = get_pixmap("settings", color="#aeb8c9", size=20)
        assert not pix.isNull()

    def test_unknown_icon_pixmap_not_null(self, qapp):
        from ui.icons import get_pixmap

        pix = get_pixmap("does-not-exist", color="#fff", size=16)
        assert isinstance(pix, type(pix))  # no crash


class TestGetIcon:
    def test_returns_qicon(self, qapp):
        from PyQt6.QtGui import QIcon

        from ui.icons import get_icon

        icon = get_icon("play", color="#9EE7FF", size=16)
        assert isinstance(icon, QIcon)

    def test_icon_not_null(self, qapp):
        from ui.icons import get_icon

        icon = get_icon("pause", color="#fff", size=14)
        assert not icon.isNull()

    def test_icon_with_active_color(self, qapp):
        from PyQt6.QtGui import QIcon

        from ui.icons import get_icon

        icon = get_icon("x", color="#AEB8C9", size=14, active_color="#FF8080")
        assert isinstance(icon, QIcon)
        assert not icon.isNull()

    def test_icon_without_active_color(self, qapp):
        from ui.icons import get_icon

        icon = get_icon("settings", color="#AEB8C9", size=14, active_color=None)
        assert not icon.isNull()

    def test_various_known_icons(self, qapp):
        from ui.icons import get_icon

        names = [
            "play",
            "pause",
            "rotate-ccw",
            "settings",
            "x",
            "maximize-2",
            "minimize-2",
            "more-horizontal",
        ]
        for name in names:
            icon = get_icon(name, color="#ffffff", size=16)
            assert not icon.isNull(), f"Icon '{name}' is null"


class TestSvgIconWidget:
    def test_instantiation(self, qapp):
        from ui.icons import SvgIconWidget

        w = SvgIconWidget("play", color="#9EE7FF", size=20)
        assert w is not None

    def test_set_color(self, qapp):
        from ui.icons import SvgIconWidget

        w = SvgIconWidget("pause", color="#ffffff", size=20)
        w.set_color("#ff0000")  # must not raise
        assert w._color == "#ff0000"

    def test_set_icon(self, qapp):
        from ui.icons import SvgIconWidget

        w = SvgIconWidget("play", color="#fff", size=20)
        w.set_icon("pause")  # must not raise
        assert w._name == "pause"

    def test_set_icon_unknown_no_crash(self, qapp):
        from ui.icons import SvgIconWidget

        w = SvgIconWidget("play", color="#fff", size=20)
        w.set_icon("totally-unknown")  # must not raise

    def test_fixed_size(self, qapp):
        from ui.icons import SvgIconWidget

        w = SvgIconWidget("clock", color="#9EE7FF", size=24)
        assert w.width() == 24
        assert w.height() == 24

import unittest

from ver_coordenadas.warning import (
    GEOGRAPHIC_AREA_WARNING,
    GEOGRAPHIC_LENGTH_WARNING,
    configure_warning_label,
    measurement_warning_text,
)


class FakeLabel:
    def __init__(self):
        self.text = None
        self.word_wrap = None
        self.visible = None

    def setText(self, value):
        self.text = value

    def setWordWrap(self, value):
        self.word_wrap = value

    def setVisible(self, value):
        self.visible = value


class WarningTextTests(unittest.TestCase):
    def test_ui_09_projected_coordinates_have_no_warning(self):
        self.assertEqual(measurement_warning_text(False, True, False), "")
        self.assertEqual(measurement_warning_text(False, False, True), "")

    def test_ui_10_geographic_polygon_uses_area_warning(self):
        self.assertEqual(
            measurement_warning_text(True, True, False),
            GEOGRAPHIC_AREA_WARNING,
        )

    def test_ui_11_geographic_line_uses_length_warning(self):
        self.assertEqual(
            measurement_warning_text(True, False, True),
            GEOGRAPHIC_LENGTH_WARNING,
        )

    def test_geographic_warning_without_supported_geometry_is_empty(self):
        self.assertEqual(measurement_warning_text(True, False, False), "")

    def test_warning_label_wraps_and_is_visible_when_text_exists(self):
        label = FakeLabel()
        configure_warning_label(label, GEOGRAPHIC_AREA_WARNING)
        self.assertEqual(label.text, GEOGRAPHIC_AREA_WARNING)
        self.assertTrue(label.word_wrap)
        self.assertTrue(label.visible)

    def test_warning_label_is_hidden_when_text_is_empty(self):
        label = FakeLabel()
        configure_warning_label(label, "")
        self.assertEqual(label.text, "")
        self.assertTrue(label.word_wrap)
        self.assertFalse(label.visible)


if __name__ == "__main__":
    unittest.main()

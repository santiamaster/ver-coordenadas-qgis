# Ver Coordenadas
# Copyright (C) 2026 Secretaría de Minería de Salta
# Desarrollado y mantenido por: Carlos Daniel Santiápichi Mastrolinardo
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los términos de la GNU General Public License publicada por la
# Free Software Foundation, versión 2 de la Licencia o, a su elección,
# cualquier versión posterior.

"""Ventana de resultado y selección del formato de coordenadas."""

from __future__ import annotations

from collections.abc import Callable

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
)

from .formatter import OutputMode, format_groups
from .geometry import CoordinateGroup, GroupKind
from .warning import configure_warning_label, measurement_warning_text


SETTINGS_PROJECTED_OUTPUT_MODE_KEY = "VerCoordenadas/output_mode"
SETTINGS_GEOGRAPHIC_OUTPUT_MODE_KEY = "VerCoordenadas/geographic_output_mode"


class CoordinatesDialog(QDialog):
    """Muestra coordenadas y medidas y permite elegir el formato correspondiente al CRS."""

    def __init__(
        self,
        coordinate_groups: list[CoordinateGroup],
        geographic_coordinates: bool,
        parent=None,
        settings_factory: Callable[[], QSettings] = QSettings,
    ) -> None:
        super().__init__(parent)
        self._coordinate_groups = coordinate_groups
        self._geographic_coordinates = geographic_coordinates
        self._settings = settings_factory()

        self.setWindowTitle("Ver coordenadas")
        self.resize(440, 480)

        self._format_selector = QComboBox(self)
        self._populate_output_modes()

        self._coordinates_text = QPlainTextEdit(self)
        self._coordinates_text.setReadOnly(True)
        self._coordinates_text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self._measurement_warning = QLabel("", self)
        has_polygon = any(
            group.kind == GroupKind.POLYGON for group in self._coordinate_groups
        )
        has_line = any(
            group.kind == GroupKind.LINE for group in self._coordinate_groups
        )
        warning_text = measurement_warning_text(
            geographic_coordinates=self._geographic_coordinates,
            has_polygon=has_polygon,
            has_line=has_line,
        )
        configure_warning_label(self._measurement_warning, warning_text)

        self._copy_status = QLabel("", self)

        close_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        close_buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Formato de coordenadas:", self))
        layout.addWidget(self._format_selector)
        layout.addWidget(self._coordinates_text)
        layout.addWidget(self._measurement_warning)
        layout.addWidget(self._copy_status)
        layout.addWidget(close_buttons)

        self._restore_output_mode()
        self._format_selector.currentIndexChanged.connect(self._refresh_output)
        self._refresh_output()

    def _populate_output_modes(self) -> None:
        """Carga únicamente los formatos compatibles con el tipo de CRS de la capa."""
        if self._geographic_coordinates:
            self._format_selector.addItem(
                "Grados, minutos y segundos (DMS)",
                OutputMode.GEOGRAPHIC_DMS.value,
            )
            self._format_selector.addItem(
                "Grados y minutos decimales (DMM)",
                OutputMode.GEOGRAPHIC_DMM.value,
            )
            self._format_selector.addItem(
                "Grados decimales (DD)",
                OutputMode.GEOGRAPHIC_DD.value,
            )
            return

        self._format_selector.addItem(
            "Gauss-Krüger (norte, este)",
            OutputMode.GAUSS_KRUGER.value,
        )
        self._format_selector.addItem(
            "Coordenadas tradicionales (este, norte)",
            OutputMode.GIS_NORMAL.value,
        )

    def _settings_key_and_default(self) -> tuple[str, str]:
        """Devuelve la clave de preferencias y el formato inicial del tipo de CRS actual."""
        if self._geographic_coordinates:
            return (
                SETTINGS_GEOGRAPHIC_OUTPUT_MODE_KEY,
                OutputMode.GEOGRAPHIC_DMS.value,
            )

        return (
            SETTINGS_PROJECTED_OUTPUT_MODE_KEY,
            OutputMode.GAUSS_KRUGER.value,
        )

    def _restore_output_mode(self) -> None:
        """Recupera el último formato válido usado para el tipo de CRS actual."""
        settings_key, default_mode = self._settings_key_and_default()
        saved_mode = self._settings.value(settings_key, default_mode, type=str)
        mode_index = self._format_selector.findData(saved_mode)

        if mode_index < 0:
            mode_index = self._format_selector.findData(default_mode)

        self._format_selector.setCurrentIndex(mode_index)

    def _current_output_mode(self) -> OutputMode:
        """Devuelve el modo seleccionado actualmente en el desplegable."""
        selected_mode = self._format_selector.currentData()
        return OutputMode(selected_mode)

    def _refresh_output(self) -> None:
        """Regenera el texto, guarda la preferencia y copia el resultado al portapapeles."""
        output_mode = self._current_output_mode()
        formatted_text = format_groups(self._coordinate_groups, output_mode)
        settings_key, _ = self._settings_key_and_default()

        self._coordinates_text.setPlainText(formatted_text)
        QApplication.clipboard().setText(formatted_text)
        self._settings.setValue(settings_key, output_mode.value)
        self._copy_status.setText("Coordenadas y medidas copiadas al portapapeles.")

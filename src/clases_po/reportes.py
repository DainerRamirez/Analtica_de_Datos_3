"""Generación de reportes de DataFrames."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


class Reportes:
    """Imprime y guarda un resumen legible de un DataFrame."""

    def reporte_descriptivo(self, df: pd.DataFrame) -> pd.DataFrame:
        """Devuelve metadata descriptiva de las columnas del DataFrame.

        ``longitud`` es la cantidad máxima de caracteres de los valores
        observados en cada columna. ``registros`` es la cantidad de filas.
        Para las columnas numéricas, los límites corresponden a sus valores
        mínimo y máximo observados. En columnas no numéricas esos límites no
        aplican y se representan como valores nulos.
        """
        self._validar_dataframe(df)
        numericas = df.select_dtypes(include="number").columns
        filas = []

        for columna in df.columns:
            serie = df[columna]
            es_numerica = columna in numericas
            nulos = int(serie.isna().sum())
            valores = serie.dropna()
            moda = valores.mode()
            porcentaje_nulos = round(nulos / len(serie) * 100, 2) if len(serie) else 0.0
            longitud = (
                valores.astype("string").str.len().max() if not valores.empty else pd.NA
            )
            filas.append(
                {
                    "columna": columna,
                    "tipo": str(serie.dtype),
                    "tipo_variable": "numérica" if es_numerica else "categórica",
                    "longitud": int(longitud) if pd.notna(longitud) else pd.NA,
                    "registros": len(serie),
                    "nulos": nulos,
                    "porcentaje_nulos": porcentaje_nulos,
                    "valores_unicos": int(serie.nunique(dropna=True)),
                    "moda": moda.iloc[0] if not moda.empty else pd.NA,
                    "limite_inferior": valores.min() if es_numerica and not valores.empty else pd.NA,
                    "limite_superior": valores.max() if es_numerica and not valores.empty else pd.NA,
                    "rango": valores.max() - valores.min()
                    if es_numerica and not valores.empty
                    else pd.NA,
                    "media": round(float(valores.mean()), 3)
                    if es_numerica and not valores.empty
                    else pd.NA,
                    "mediana": valores.median() if es_numerica and not valores.empty else pd.NA,
                    "desviacion_estandar": round(float(valores.std()), 3)
                    if es_numerica and len(valores) > 1
                    else pd.NA,
                }
            )

        return pd.DataFrame(filas).set_index("columna")

    def generar_reporte(self, df: pd.DataFrame) -> str:
        """Genera el contenido textual del reporte."""
        self._validar_dataframe(df)
        numericas = df.select_dtypes(include="number")
        lineas = [
            "REPORTE DEL DATAFRAME",
            "=" * 60,
            f"Filas: {len(df)}",
            f"Columnas: {len(df.columns)}",
            f"Duplicados: {int(df.duplicated().sum())}",
            "",
            "Columnas y tipos:",
            *[f"- {columna}: {tipo}" for columna, tipo in df.dtypes.items()],
            "",
            "Valores nulos por columna:",
            *[f"- {columna}: {cantidad}" for columna, cantidad in df.isna().sum().items()],
        ]

        if not numericas.empty:
            lineas += [
                "",
                "Estadísticas numéricas:",
                numericas.describe().round(3).to_string(),
            ]

        return "\n".join(lineas) + "\n"

    def imprimir_reporte(self, df: pd.DataFrame) -> None:
        """Imprime en la consola el reporte del DataFrame."""
        print(self.generar_reporte(df), end="")

    def guardar_reporte(self, df: pd.DataFrame, ruta: str | Path) -> Path:
        """Guarda el reporte en un archivo de texto y devuelve su ruta."""
        path = Path(ruta)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generar_reporte(df), encoding="utf-8")
        return path

    @staticmethod
    def _validar_dataframe(df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df debe ser un pandas.DataFrame.")
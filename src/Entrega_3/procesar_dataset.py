"""Prepara el dataset de salarios y genera las tablas descriptivas de AE3."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

import pandas as pd


ENTREGA_DIR: Final[Path] = Path(__file__).resolve().parent
SRC_DIR: Final[Path] = ENTREGA_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from clases_po.reportes import Reportes


RAW_PATH: Final[Path] = ENTREGA_DIR / "datos" / "demo-salaries-original.csv"
PREPARED_PATH: Final[Path] = ENTREGA_DIR / "datos" / "demo-salaries-preparado.csv"
RESULTS_DIR: Final[Path] = ENTREGA_DIR / "resultados"

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "work_year",
    "experience_level",
    "employment_type",
    "job_title",
    "salary",
    "salary_currency",
    "salary_in_usd",
    "employee_residence",
    "remote_ratio",
    "company_location",
    "company_size",
)

EXPERIENCE_LABELS: Final[dict[str, str]] = {
    "EN": "Inicial",
    "MI": "Intermedio",
    "SE": "Senior",
    "EX": "Ejecutivo",
}
EMPLOYMENT_LABELS: Final[dict[str, str]] = {
    "FT": "Tiempo completo",
    "PT": "Tiempo parcial",
    "CT": "Contrato",
    "FL": "Freelance",
}
COMPANY_SIZE_LABELS: Final[dict[str, str]] = {
    "S": "Pequeña",
    "M": "Mediana",
    "L": "Grande",
}
REMOTE_LABELS: Final[dict[int, str]] = {
    0: "Presencial",
    50: "Híbrido",
    100: "Remoto",
}


def _normalizar_categoria(
    serie: pd.Series, equivalencias: dict[str, str], columna: str
) -> pd.Series:
    normalizada = serie.astype("string").str.strip()
    desconocidas = sorted(set(normalizada.dropna()) - set(equivalencias))
    if desconocidas:
        raise ValueError(
            f"Categorías no contempladas en {columna}: {desconocidas}"
        )
    return normalizada.map(equivalencias)


def cargar_y_transformar(
    ruta_origen: str | Path = RAW_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga una copia de referencia y devuelve el DataFrame normalizado."""
    df_original = pd.read_csv(ruta_origen)
    faltantes = sorted(set(REQUIRED_COLUMNS) - set(df_original.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en el CSV: {faltantes}")

    df = df_original.copy(deep=True)
    columnas_numericas = ("work_year", "salary", "salary_in_usd", "remote_ratio")
    for columna in columnas_numericas:
        convertida = pd.to_numeric(df[columna], errors="raise")
        no_enteros = convertida.notna() & (convertida % 1 != 0)
        if no_enteros.any():
            raise ValueError(f"{columna} contiene valores que no son enteros.")
        df[columna] = convertida.astype("Int64")

    df["experience_level"] = _normalizar_categoria(
        df["experience_level"], EXPERIENCE_LABELS, "experience_level"
    )
    df["employment_type"] = _normalizar_categoria(
        df["employment_type"], EMPLOYMENT_LABELS, "employment_type"
    )
    df["company_size"] = _normalizar_categoria(
        df["company_size"], COMPANY_SIZE_LABELS, "company_size"
    )

    ratios_desconocidos = sorted(
        set(df["remote_ratio"].dropna().astype(int)) - set(REMOTE_LABELS)
    )
    if ratios_desconocidos:
        raise ValueError(
            f"Valores de remote_ratio no contemplados: {ratios_desconocidos}"
        )
    df["remote_work_mode"] = df["remote_ratio"].map(REMOTE_LABELS).astype("string")

    if (df["salary_in_usd"].dropna() < 0).any():
        raise ValueError("salary_in_usd no puede contener valores negativos.")

    return df_original, df


def describir_cambios(
    df_original: pd.DataFrame, df_preparado: pd.DataFrame
) -> pd.DataFrame:
    """Resume filas, columnas y nulos antes y después de la preparación."""
    filas = []
    for etapa, df in (("Original", df_original), ("Preparado", df_preparado)):
        filas.append(
            {
                "etapa": etapa,
                "filas": len(df),
                "columnas": len(df.columns),
                "duplicados_exactos": int(df.duplicated().sum()),
                "valores_nulos": int(df.isna().sum().sum()),
            }
        )
    return pd.DataFrame(filas)


def crear_tablas_resultados(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Calcula una tabla por cada pregunta de negocio y valida sus totales."""
    salario = "salary_in_usd"
    principal = (
        df.groupby(
            ["experience_level", "remote_work_mode", "company_size"],
            dropna=False,
            observed=True,
        )
        .agg(
            cantidad_registros=(salario, "count"),
            salario_usd_mediana=(salario, "median"),
            salario_usd_promedio=(salario, "mean"),
            salario_usd_q1=(salario, lambda valores: valores.quantile(0.25)),
            salario_usd_q3=(salario, lambda valores: valores.quantile(0.75)),
        )
        .reset_index()
        .rename(
            columns={
                "experience_level": "nivel_experiencia",
                "remote_work_mode": "modalidad_trabajo",
                "company_size": "tamano_empresa",
            }
        )
        .sort_values(
            ["nivel_experiencia", "modalidad_trabajo", "tamano_empresa"],
            na_position="last",
        )
        .reset_index(drop=True)
    )

    apoyo_1 = (
        df.groupby(
            ["work_year", "experience_level", "employment_type"],
            dropna=False,
            observed=True,
        )
        .size()
        .rename("cantidad_registros")
        .reset_index()
        .rename(
            columns={
                "work_year": "anio_referencia",
                "experience_level": "nivel_experiencia",
                "employment_type": "tipo_empleo",
            }
        )
        .sort_values(
            ["anio_referencia", "nivel_experiencia", "tipo_empleo"],
            na_position="last",
        )
        .reset_index(drop=True)
    )

    apoyo_2 = (
        df.groupby("job_title", dropna=False, observed=True)
        .agg(
            cantidad_registros=(salario, "count"),
            salario_usd_mediano=(salario, "median"),
        )
        .reset_index()
        .rename(columns={"job_title": "cargo"})
        .sort_values(
            ["cantidad_registros", "cargo"],
            ascending=[False, True],
            na_position="last",
        )
        .reset_index(drop=True)
    )

    apoyo_3 = (
        df.groupby("work_year", dropna=False, observed=True)
        .agg(
            cantidad_registros=(salario, "count"),
            salario_usd_mediano=(salario, "median"),
        )
        .reset_index()
        .rename(columns={"work_year": "anio_referencia"})
        .sort_values("anio_referencia")
        .reset_index(drop=True)
    )
    apoyo_3["variacion_mediana_usd_vs_anio_anterior"] = (
        apoyo_3["salario_usd_mediano"].diff()
    )
    apoyo_3["variacion_mediana_porcentual_vs_anio_anterior"] = (
        apoyo_3["salario_usd_mediano"].pct_change() * 100
    )

    tablas = {
        "pregunta_principal_salarios_por_grupo": principal,
        "pregunta_apoyo_1_registros_por_anio_experiencia_empleo": apoyo_1,
        "pregunta_apoyo_2_cargos_por_registros_y_mediana": apoyo_2,
        "pregunta_apoyo_3_salario_mediano_por_anio": apoyo_3,
    }

    for nombre, tabla in tablas.items():
        if tabla.empty:
            raise ValueError(f"La tabla {nombre} no contiene resultados.")

    total = len(df)
    for nombre in (
        "pregunta_principal_salarios_por_grupo",
        "pregunta_apoyo_1_registros_por_anio_experiencia_empleo",
        "pregunta_apoyo_2_cargos_por_registros_y_mediana",
        "pregunta_apoyo_3_salario_mediano_por_anio",
    ):
        suma = int(tablas[nombre]["cantidad_registros"].sum())
        if suma != total:
            raise AssertionError(
                f"Los conteos de {nombre} suman {suma}, pero el DataFrame tiene {total} filas."
            )

    return tablas


def exportar_resultados(
    df: pd.DataFrame,
    tablas: dict[str, pd.DataFrame],
    directorio_resultados: str | Path = RESULTS_DIR,
    ruta_preparado: str | Path = PREPARED_PATH,
) -> dict[str, Path]:
    """Escribe el dataset, las cuatro tablas y el resumen descriptivo."""
    destino_resultados = Path(directorio_resultados)
    destino_preparado = Path(ruta_preparado)
    destino_resultados.mkdir(parents=True, exist_ok=True)
    destino_preparado.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(destino_preparado, index=False, encoding="utf-8-sig")
    rutas = {"dataset_preparado": destino_preparado}
    for nombre, tabla in tablas.items():
        ruta = destino_resultados / f"{nombre}.csv"
        tabla.to_csv(ruta, index=False, encoding="utf-8-sig")
        rutas[nombre] = ruta

    ruta_resumen = destino_resultados / "resumen_dataframe.txt"
    Reportes().guardar_reporte(df, ruta_resumen)
    rutas["resumen_dataframe"] = ruta_resumen
    return rutas


def ejecutar_flujo() -> tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame], dict[str, Path]
]:
    """Ejecuta la preparación, el análisis y las exportaciones completas."""
    df_original, df_preparado = cargar_y_transformar()
    cambios = describir_cambios(df_original, df_preparado)
    tablas = crear_tablas_resultados(df_preparado)
    rutas = exportar_resultados(df_preparado, tablas)
    return df_original, df_preparado, cambios, tablas, rutas


if __name__ == "__main__":
    _, preparado, cambios, tablas_generadas, archivos = ejecutar_flujo()
    print(cambios.to_string(index=False))
    print(f"\nDataFrame preparado: {preparado.shape[0]} filas, {preparado.shape[1]} columnas")
    print("\nArchivos generados:")
    for nombre, ruta in archivos.items():
        print(f"- {nombre}: {ruta.relative_to(ENTREGA_DIR)}")
    print(f"\nFilas en cada tabla: { {nombre: len(tabla) for nombre, tabla in tablas_generadas.items()} }")

# Proyecto_analitica_3

## Entrega AE3: preparación y análisis descriptivo de salarios

La carpeta [`src/Entrega_3`](src/Entrega_3/) conserva una copia del CSV de AE2 y contiene el notebook ejecutado, el código Python reutilizado y las evidencias generadas. La entrega de AE2 no se modifica.

### Necesidad y preguntas

El análisis responde a una necesidad hipotética del equipo de talento humano: comparar salarios registrados en USD para cargos de datos y tecnología, considerando experiencia, modalidad de trabajo remoto y tamaño de empresa. No se afirma que la necesidad corresponda a una empresa real ni que los datos representen todo el mercado.

1. ¿Cómo se comparan los salarios en USD por nivel de experiencia, modalidad de trabajo remoto y tamaño de empresa?
2. ¿Cuántos registros hay por año de referencia (`work_year`), nivel de experiencia y tipo de empleo?
3. ¿Qué cargos tienen más registros y cuál es su salario mediano en USD?
4. ¿Cómo cambia el salario mediano en USD entre los años cubiertos?

El dataset contiene `work_year` (año de referencia), no una fecha de pago exacta; por eso las preguntas que inicialmente hablaban de año de pago se interpretan como comparaciones por el año registrado. El periodo disponible es 2020–2023. El análisis es descriptivo y no utiliza modelos predictivos.

### Transformaciones y controles

- Se lee el CSV original de AE2 sin modificarlo y se conserva una copia en `src/Entrega_3/datos/demo-salaries-original.csv`.
- Se verifican las columnas requeridas, se convierten `work_year`, `salary`, `salary_in_usd` y `remote_ratio` a tipos enteros anulables y se comprueba que los salarios en USD no sean negativos.
- Se traducen a etiquetas legibles los códigos de experiencia (`EN`, `MI`, `SE`, `EX`), tipo de empleo (`FT`, `PT`, `CT`, `FL`) y tamaño de empresa (`S`, `M`, `L`). Se agrega `remote_work_mode` a partir de `remote_ratio` (`0` presencial, `50` híbrido, `100` remoto). Las variables originales numéricas se conservan.
- No se imputan nulos ni se eliminan registros. En el archivo fuente hay 3.755 filas y 11 columnas, sin nulos y con 1.171 ocurrencias posteriores de filas exactamente repetidas (`duplicated()`; no incluye la primera aparición). Como no hay una clave que permita distinguir repeticiones erróneas, se conservan. El resultado tiene las mismas filas y una columna derivada adicional.
- Los conteos de las cuatro tablas se verifican contra el total de registros antes de exportar.

### Archivos AE3

- Notebook reproducible y ejecutado: [`Semana_3_AE3.ipynb`](src/Entrega_3/Semana_3_AE3.ipynb).
- Código Python: [`procesar_dataset.py`](src/Entrega_3/procesar_dataset.py).
- Documento Word actualizado de AE2: [`Avance_AE3.docx`](src/Entrega_3/Avance_AE3.docx). El archivo de AE2 se conserva sin cambios.
- Dataset original: [`demo-salaries-original.csv`](src/Entrega_3/datos/demo-salaries-original.csv).
- Dataset preparado: [`demo-salaries-preparado.csv`](src/Entrega_3/datos/demo-salaries-preparado.csv).
- Tabla de la pregunta principal: [`pregunta_principal_salarios_por_grupo.csv`](src/Entrega_3/resultados/pregunta_principal_salarios_por_grupo.csv).
- Tabla de apoyo 1: [`pregunta_apoyo_1_registros_por_anio_experiencia_empleo.csv`](src/Entrega_3/resultados/pregunta_apoyo_1_registros_por_anio_experiencia_empleo.csv).
- Tabla de apoyo 2: [`pregunta_apoyo_2_cargos_por_registros_y_mediana.csv`](src/Entrega_3/resultados/pregunta_apoyo_2_cargos_por_registros_y_mediana.csv).
- Tabla de apoyo 3: [`pregunta_apoyo_3_salario_mediano_por_anio.csv`](src/Entrega_3/resultados/pregunta_apoyo_3_salario_mediano_por_anio.csv).
- Resumen regenerado automáticamente: [`resumen_dataframe.txt`](src/Entrega_3/resultados/resumen_dataframe.txt).

### Ejecución

Desde la raíz del proyecto, instala las dependencias y ejecuta el notebook celda por celda:

```powershell
python -m pip install -r requirements.txt
```

Para generar los CSV y el resumen desde la terminal:

```powershell
python src\Entrega_3\procesar_dataset.py
```

El notebook y el script utilizan rutas relativas al proyecto; no requieren descargar nuevamente el dataset de Hugging Face.

### Fuente del dataset y limitaciones

El CSV procede de la copia que ya estaba en AE2 y cuyo notebook identifica como `Einstellung/demo-salaries` en Hugging Face. Las dos copias existentes en AE2 y sincronicas coinciden. El conjunto contiene registros de 2020 a 2023; no se conoce aquí su representatividad, metodología de recolección ni si observaciones repetidas son duplicados accidentales. Los países y la composición de cargos no se controlan en estas comparaciones, y no se ajusta por inflación ni paridad de poder adquisitivo; la unidad monetaria común no elimina esas diferencias. Los salarios en otras monedas se conservan en `salary` y `salary_currency`; las comparaciones de resultados utilizan únicamente `salary_in_usd`. No se incorporan fuentes externas ni se infiere rentabilidad, competitividad de mercado o causalidad.
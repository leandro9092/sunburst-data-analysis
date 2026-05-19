#  Proyecto: Análisis de Datos del Incidente SolarWinds SUNBURST

Este repositorio contiene el desarrollo del proyecto práctico para la asignatura **Gestión de Datos** (3er Semestre) de la **Universidad de San Buenaventura**. El objetivo principal es modelar, auditar y detectar patrones anómalos de ciberseguridad utilizando el marco de referencia **DAMA DMBOK** y programación en **Python**, tomando como caso de estudio el ataque a la cadena de suministro de SolarWinds Orion.

---

## Integrantes y Roles Asignados

* **[Jose Daniel Patiño Maussa ]** - **ROL 1: Diseñador de Datos** - Modelado y Generación
* **[Leandro Zapata Muñoz]** - **ROL 2: Analista de Calidad** - Validación y Detección de Patrones
* **[Miguel Angel Garcia Agudelo]** - **ROL 3: Integrador de Datos** - Consolidación y Mapeo al Ciclo de Vida

---

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.12+
* **Librerías Clave:** * `pandas` (Manipulación de estructuras de datos y alineación relacional)
    * `numpy` (Generación matricial y lógica aleatoria sembrada)
    * `faker` (Simulación de datos sintéticos institucionales)
    * `matplotlib` & `seaborn` (Renderizado de paneles estadísticos y cuadros de mando)
* **Entornos:** Jupyter Notebooks & Scripts de terminal Python (.py)

---

## Estructura del Repositorio

El proyecto sigue una organización limpia y scannable para garantizar la reproducibilidad técnica:


sunburst-data-analysis/
├── README.md                 <- Este archivo con la documentación general.
├── requirements.txt         <- Listado de dependencias y librerías de Python.
├── data/                    <- Archivos de datos generados en formato CSV.
│   ├── clientes.csv
│   ├── eventos_ciclo_vida.csv
│   ├── eventos_seguridad.csv
│   ├── instalaciones.csv
│   ├── reporte_calidad.csv
|   ├── resumen_impacto.csv
|   └── versiones_software.csv
├── notebooks/               <- Jupyter Notebooks explicativos con análisis paso a paso.
│   ├── Rol1_Modelado.ipynb
│   └── Rol2_Calidad.ipynb
│   └── rol3_Integracion.ipynb
├── scripts/                 <- Scripts phyton.
│   ├── rol1_generacion_datos.py
│   └── rol2_calidad_datos.py
|   └── rol3_integracion.py
├── visualizations/          <- Gráficos exportados en formato PNG.
│   ├── dashboard_sunburst.png
│   ├── grafico1_sunburst_realidad.png
│   ├── grafico2_tipos_eventos.png
│   ├── grafico3_severidad_ataques.png
│   └── grafico4_reporte_calidad.png 
└── docs/                    <- Diccionario de datos e informe final de auditoría.

---

## Instrucciones de instalación y ejecución

**Crear y activar un entorno virtual aislado:**

*En Windows (PowerShell / CMD):*

* bash 

crear 

python -m venv venv

activar 
 
.\venv\Scripts\activate

*En macOS / Linux:*

* bash 

python3 -m venv venv
source venv/bin/activate

**Instalar todas las dependencias requeridas:**

*Este comando instalará de golpe las versiones estables de pandas, numpy, faker, matplotlib y seaborn especificadas en el archivo de requerimientos.*

pip install -r requirements.txt

* Flujo de Ejecución

*El proyecto está diseñado de forma modular. Para que el análisis funcione, debes ejecutar los scripts respetando la jerarquía de los roles*
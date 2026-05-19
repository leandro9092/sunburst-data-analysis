#  Diccionario de Datos — Proyecto  SUNBURST

Este documento técnico detalla las especificaciones relacionales, tipos de datos físicos en Python/Pandas, restricciones de dominio, claves y las reglas de negocio codificadas a lo largo de los tres roles del proyecto.

---

## 🗺️ Mapa de Relaciones Lógicas (Arquitectura)
* `clientes.csv` **(1) ─── (N)** `instalaciones.csv`
* `versiones_software.csv` **(1) ─── (N)** `instalaciones.csv`
* `instalaciones.csv` **(1) ─── (N)** `eventos_seguridad.csv`
* `reporte_calidad.csv` (Matriz analítica aislada de control de calidad DAMA)

---

## 1. Tabla: `clientes.csv` (Datos Maestros)
* **Origen:** Generado sintéticamente por el **Rol 1** utilizando la librería `Faker` (Semilla: 42).
* **Descripción:** Almacena el universo de organizaciones evaluadas dentro de la infraestructura institucional expuesta.
* **Tamaño:** 50 registros únicos.

| Nombre del Campo | Tipo de Dato (Pandas) | Clave | Restricciones / Reglas de Dominio | Descripción Técnica |
| :--- | :--- | :--- | :--- | :--- |
| `cliente_id` | `object` (String) | **PK** | Formato único indexado: `CLI-XXXX` (relleno con ceros a la izquierda). No nulo. | Identificador unívoco del cliente institucional. |
| `nombre_organizacion` | `object` (String) | | Generado mediante `fake.company()`. | Nombre legal o comercial de la entidad. |
| `sector_industrial` | `object` (String) | | Dominio cerrado: `Gobierno`, `Finanzas`, `Tecnología`, `Salud`, `Educación`, `Energía`. | Sector económico donde opera el cliente. |
| `pais` | `object` (String) | | Generado mediante `fake.country()`. | País sede donde se encuentra la infraestructura analizada. |
| `nivel_criticidad` | `object` (String) | | Dominio cerrado con pesos probabilísticos: `Bajo`, `Medio`, `Alto`, `Crítico`. | Clasificación del nivel de riesgo ante incidentes de ciberseguridad. |

---

## 2. Tabla: `versiones_software.csv` (Datos Maestros Catalogados)
* **Origen:** Diseñado por el **Rol 1** con base en el historial cronológico del ataque real a la cadena de suministro de SolarWinds.
* **Descripción:** Catálogo de versiones comerciales de la plataforma Orion liberadas entre 2019 y 2021.
* **Tamaño:** 8 registros fijos.

| Nombre del Campo | Tipo de Dato (Pandas) | Clave | Restricciones / Reglas de Dominio | Descripción Técnica |
| :--- | :--- | :--- | :--- | :--- |
| `version_id` | `object` (String) | **PK** | Formato secuencial estricto: `VER-XXXX`. No nulo. | Identificador único de la compilación empaquetada. |
| `numero_version` | `object` (String) | | Valores reales del caso: `2019.2`, `2019.4 HF 1` hasta `2020.2.1 HF 2`. | Nomenclatura comercial del paquete de software Orion. |
| `fecha_liberacion` | `object` (String / Date) | | Formato cronológico ISO: `YYYY-MM-DD`. | Fecha oficial de distribución en el mercado global. |
| `contiene_sunburst` | `bool` (Boolean) | | Valores: `True` (vulnerable/infectada), `False` (limpia). | Bandera lógica de seguridad; determina si la versión posee el backdoor inyectado. |

---

## 3. Tabla: `instalaciones.csv` (Tabla de Hechos Intermedia)
* **Origen:** Mapeado por el **Rol 1** mediante relaciones aleatorias cruzadas controladas.
* **Descripción:** Registra las instalaciones físicas activas donde los clientes desplegaron versiones específicas de Orion en entornos empresariales.
* **Tamaño:** 100 registros.

| Nombre del Campo | Tipo de Dato (Pandas) | Clave | Restricciones / Reglas de Dominio | Descripción Técnica |
| :--- | :--- | :--- | :--- | :--- |
| `instalacion_id` | `object` (String) | **PK** | Formato secuencial: `INS-XXXX`. No nulo. | Identificador único de la infraestructura instalada. |
| `cliente_id` | `object` (String) | **FK** | Debe coincidir estrictamente con una PK válida de `clientes.csv`. | Referencia al cliente que ejecutó la instalación. |
| `version_id` | `object` (String) | **FK** | Debe coincidir estrictamente con una PK válida de `versiones_software.csv`. | Referencia a la versión del producto instalada en la máquina. |
| `fecha_instalacion` | `object` (String / Date) | | Formato ISO: `YYYY-MM-DD`. Debe ser posterior a la fecha de liberación del software. | Fecha del despliegue operacional local. |
| `entorno_despliegue` | `object` (String) | | Dominio cerrado con pesos: `Producción` (70%), `Pruebas` (20%), `Desarrollo` (10%). | Tipo de ambiente lógico donde corre el software. |

---

## 4. Tabla: `eventos_seguridad.csv` (Logs Operacionales y Datos Analíticos)
* **Origen:** Construido por el **Rol 2**, consumiendo la telemetría de instalaciones del Rol 1 e inyectando impurezas de datos artificiales.
* **Descripción:** Log de tráfico y alertas de auditoría de red donde conviven el ruido operativo cotidiano y los ataques reales de exfiltración de datos.
* **Tamaño:** 200 registros.

| Nombre del Campo | Tipo de Dato (Pandas) | Clave | Restricciones / Reglas de Dominio / Impurezas Inyectadas | Descripción Técnica |
| :--- | :--- | :--- | :--- | :--- |
| `evento_id` | `object` (String) | **PK** | Formato correlativo: `EVT-XXXX`. No nulo. | Identificador único del log de red. |
| `instalacion_id` | `object` (String) | **FK** | **Falla de Integridad Referencial:** Contiene 5 registros con el valor `INST-9999` (ID inexistente para simular huérfanos). | Referencia al nodo/instalación que generó el log de alerta. |
| `timestamp` | `object` (String / DateTime) | | **Falla de Exactitud:** Contiene 1 registro con el año erróneo `2035-05-18` (fuera del umbral histórico). | Marca de tiempo (fecha y hora) del registro del evento. |
| `tipo_evento` | `object` (String) | | **Falla de Completitud:** Contiene 4 registros nulos (`NaN`). Valores válidos: `Acceso Exitoso`, `Escaneo de Puertos`, `Falla de Autenticación`, `Tráfico de Red Anómalo`, `Modificación de Registro`. | Naturaleza o tipo de alerta detectada por el sensor. |
| `severidad` | `object` (String) | | Dominio cerrado uniforme: `Baja`, `Media`, `Alta`, `Crítica`. | Nivel de urgencia o impacto técnico de la alerta. |
| `es_anomalo` | `bool` (Boolean) | | **Regla de Álgebra Relacional (Lógica Rol 2):** Es `True` si (`tipo_evento` == 'Tráfico de Red Anómalo') & (`severidad` $\in$ ['Alta', 'Crítica']) & (`contiene_sunburst` == `True`). De lo contrario, `False`. | Atributo derivado/analítico que aísla de forma matemática los ataques dirigidos reales. |

---

## 5. Tabla: `reporte_calidad.csv` (Cuadro de Mando de Gobernanza DAMA)
* **Origen:** Resultado automático del módulo de auditoría de código del **Rol 2**.
* **Descripción:** Métricas cuantitativas que evalúan la calidad de los datos del proyecto frente a los requerimientos del negocio.
* **Tamaño:** Dinámico según las dimensiones analizadas.

| Nombre del Campo | Tipo de Dato (Pandas) | Restricciones / Reglas de Dominio | Descripción Técnica |
| :--- | :--- | :--- | :--- |
| `tabla` | `object` (String) | Nombre de la entidad analizada (`eventos_seguridad`). | Identifica el origen del set evaluado. |
| `columna` | `object` (String) | Atributos evaluados (`tipo_evento`, `timestamp`, `instalacion_id`). | Variable específica que se sometió a las reglas de control. |
| `metrica` | `object` (String) | Dimensiones DAMA estrictas: `Completitud`, `Exactitud`, `Consistencia`, `Integridad Referencial`. | Tipo de dimensión de calidad analizada en el framework. |
| `valor_actual` | `float64` (Porcentaje) | Escala numérica porcentual de `0.0` a `100.0`. | Porcentaje real de datos limpios calculados en la auditoría. |
| `umbral` | `float64` (Porcentaje) | Valor fijo de aceptación: `100.0` (Exigencia del negocio). | Meta de calidad mínima estipulada por la gobernanza de datos. |
| `estado` | `object` (String) | Evaluación lógica: `Aprobado` (si cumple el umbral) o `Fallo` (si posee impurezas). | Estado final del cumplimiento regulatorio de la variable. |

---

##  Ciclo de Vida del Dato y Enfoque del Rol 3 (Integrador de Datos)
El **Rol 3** ejecuta la fase de *Integración y Analítica Avanzada* del ciclo DAMA DMBOK. Une las tablas maestras de infraestructura y los logs operacionales a través de combinaciones de álgebra relacional (`pd.merge`), mapeando los datos consolidados en un cuadro de mando unificado (Dashboard Integrado en `visualizations/`) con el fin de generar los insights definitivos de ciberseguridad para la toma de decisiones institucionales.
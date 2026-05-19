"""
rol1_generacion_datos.py
========================
Rol 1 - Diseñador de Datos: Generación de datos sintéticos para el análisis
del incidente SUNBURST de SolarWinds.

Caso: SolarWinds se enfrenta a SUNBURST (B)
Curso: Gestión de Datos - Universidad de San Buenaventura
Marco: DAMA DMBOK

Autor: Rol 1 - Diseñador de Datos
Descripción:
    Este script genera tres DataFrames sintéticos que simulan los datos
    involucrados en el incidente SUNBURST:
      1. clientes        (50 registros)
      2. versiones_software (8 registros)
      3. instalaciones   (100 registros)

    Los datos son coherentes con el contexto real del caso (2019-2021),
    incluyendo la distinción entre versiones vulnerables y no vulnerables.
"""

import pandas as pd
import numpy as np
from faker import Faker
import os

# ── Reproducibilidad ────────────────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)
fake = Faker("es_MX")
fake.seed_instance(SEED)

# ── Rutas de salida ──────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# FUNCIÓN 1: Generar DataFrame de CLIENTES
# ============================================================
def generar_clientes(n: int = 50) -> pd.DataFrame:
    """
    Genera un DataFrame con n clientes ficticios que utilizaban
    la Plataforma Orion de SolarWinds.

    Parámetros
    ----------
    n : int
        Número de registros a generar (por defecto 50).

    Retorna
    -------
    pd.DataFrame con columnas:
        cliente_id, nombre_organizacion, tipo_org, pais,
        sector, criticidad
    """
    # Listas de dominio basadas en el caso real
    tipos_org = ["Gobierno Federal", "Gobierno Estatal", "Empresa Privada",
                 "Empresa de Tecnología", "Institución Financiera",
                 "Organización Militar", "Universidad"]

    sectores = ["Energía", "Defensa", "Finanzas", "Tecnología",
                "Salud", "Educación", "Telecomunicaciones",
                "Manufactura", "Retail", "Gobierno"]

    paises = (
        ["Estados Unidos"] * 30     # mayoría de afectados era EE.UU.
        + ["Reino Unido"] * 5
        + ["Canadá"] * 5
        + ["Alemania"] * 3
        + ["Australia"] * 3
        + ["Francia"] * 2
        + ["Israel"] * 2
    )

    criticidades = ["CRÍTICA", "ALTA", "MEDIA", "BAJA"]
    pesos_criticidad = [0.25, 0.35, 0.30, 0.10]  # más peso en alta/crítica

    registros = []
    for i in range(1, n + 1):
        registros.append({
            "cliente_id": f"CLI-{i:04d}",
            "nombre_organizacion": fake.company(),
            "tipo_org": np.random.choice(tipos_org),
            "pais": np.random.choice(paises),
            "sector": np.random.choice(sectores),
            "criticidad": np.random.choice(
                criticidades, p=pesos_criticidad
            ),
        })

    df = pd.DataFrame(registros)
    return df


# ============================================================
# FUNCIÓN 2: Generar DataFrame de VERSIONES DE SOFTWARE
# ============================================================
def generar_versiones_software() -> pd.DataFrame:
    """
    Genera el DataFrame de las 8 versiones relevantes de la
    Plataforma Orion de SolarWinds mencionadas en el caso SUNBURST.

    Las versiones 2019.4 (anteriores a HF5) y 2020.2 / 2020.2 HF1
    son las que contenían el malware SUNBURST.

    Retorna
    -------
    pd.DataFrame con columnas:
        version_id, nombre_version, fecha_release,
        contiene_sunburst, fecha_compilacion
    """
    versiones = [
        # ── Versiones VULNERABLES (contienen SUNBURST) ──────────────────
        {
            "version_id": "VER-001",
            "nombre_version": "Orion 2019.4",
            "fecha_release": "2019-10-15",
            "contiene_sunburst": True,   # AA inyectó código desde oct 2019
            "fecha_compilacion": "2019-10-10",
        },
        {
            "version_id": "VER-002",
            "nombre_version": "Orion 2019.4 HF1",
            "fecha_release": "2019-12-01",
            "contiene_sunburst": True,
            "fecha_compilacion": "2019-11-28",
        },
        {
            "version_id": "VER-003",
            "nombre_version": "Orion 2019.4 HF2",
            "fecha_release": "2020-01-15",
            "contiene_sunburst": True,
            "fecha_compilacion": "2020-01-12",
        },
        {
            "version_id": "VER-004",
            "nombre_version": "Orion 2020.2",
            "fecha_release": "2020-02-25",   # compilado el 20/02/2020 según caso
            "contiene_sunburst": True,
            "fecha_compilacion": "2020-02-20",
        },
        {
            "version_id": "VER-005",
            "nombre_version": "Orion 2020.2 HF1",
            "fecha_release": "2020-04-10",
            "contiene_sunburst": True,
            "fecha_compilacion": "2020-04-07",
        },
        # ── Versiones SEGURAS (no contienen SUNBURST) ────────────────────
        {
            "version_id": "VER-006",
            "nombre_version": "Orion 2019.4 HF5",
            "fecha_release": "2020-03-26",   # Hotfix 5 disponible 26/03/2020
            "contiene_sunburst": False,
            "fecha_compilacion": "2020-03-24",
        },
        {
            "version_id": "VER-007",
            "nombre_version": "Orion 2020.2.1",
            "fecha_release": "2020-12-15",   # parche lanzado 15/12/2020
            "contiene_sunburst": False,
            "fecha_compilacion": "2020-12-13",
        },
        {
            "version_id": "VER-008",
            "nombre_version": "Orion 2020.2.1 HF2",
            "fecha_release": "2021-01-11",
            "contiene_sunburst": False,
            "fecha_compilacion": "2021-01-09",
        },
    ]

    df = pd.DataFrame(versiones)
    df["fecha_release"] = pd.to_datetime(df["fecha_release"])
    df["fecha_compilacion"] = pd.to_datetime(df["fecha_compilacion"])
    return df


# ============================================================
# FUNCIÓN 3: Generar DataFrame de INSTALACIONES
# ============================================================
def generar_instalaciones(
    df_clientes: pd.DataFrame,
    df_versiones: pd.DataFrame,
    n: int = 100,
) -> pd.DataFrame:
    """
    Genera n registros de instalaciones que relacionan clientes
    con versiones de software instaladas.

    Lógica de negocio incorporada:
    - ~18 000 instalaciones activadas en el caso real → aquí se escala a 100
    - La mayoría de instalaciones usaban versiones vulnerables (realismo)
    - Solo una fracción pequeña resultó realmente comprometida
      (simulado con nivel_datos_sensibles muy alto en pocos registros)

    Parámetros
    ----------
    df_clientes   : DataFrame de clientes
    df_versiones  : DataFrame de versiones
    n             : número de instalaciones a generar

    Retorna
    -------
    pd.DataFrame con columnas:
        instalacion_id, cliente_id, version_id,
        fecha_instalacion, nivel_datos_sensibles
    """
    ids_clientes = df_clientes["cliente_id"].tolist()
    ids_versiones = df_versiones["version_id"].tolist()

    # Pesos: las versiones vulnerables tienen más instalaciones históricas
    pesos_version = [0.15, 0.15, 0.10, 0.20, 0.10, 0.10, 0.12, 0.08]

    niveles = ["BAJO", "MEDIO", "ALTO", "MUY_ALTO"]
    pesos_nivel = [0.30, 0.40, 0.20, 0.10]

    registros = []
    for i in range(1, n + 1):
        version_elegida = np.random.choice(ids_versiones, p=pesos_version)

        # Fecha de instalación coherente con la fecha de release de la versión
        fecha_release = df_versiones.loc[
            df_versiones["version_id"] == version_elegida, "fecha_release"
        ].values[0]
        fecha_release_dt = pd.Timestamp(fecha_release)

        # Instalar hasta 18 meses después del release
        dias_offset = np.random.randint(0, 540)
        fecha_instalacion = fecha_release_dt + pd.Timedelta(days=int(dias_offset))

        # No permitir fechas posteriores al cierre del análisis (mayo 2021)
        fecha_tope = pd.Timestamp("2021-05-07")
        if fecha_instalacion > fecha_tope:
            fecha_instalacion = fecha_tope

        registros.append({
            "instalacion_id": f"INS-{i:04d}",
            "cliente_id": np.random.choice(ids_clientes),
            "version_id": version_elegida,
            "fecha_instalacion": fecha_instalacion.date(),
            "nivel_datos_sensibles": np.random.choice(
                niveles, p=pesos_nivel
            ),
        })

    df = pd.DataFrame(registros)
    return df


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def main():
    """
    Orquesta la generación de los tres DataFrames y exporta
    cada uno como archivo CSV en la carpeta /data.
    """
    print("=" * 60)
    print("  ROL 1 – Generación de Datos Sintéticos SUNBURST")
    print("=" * 60)

    # 1. Clientes
    print("\n[1/3] Generando DataFrame de clientes (50 registros)...")
    df_clientes = generar_clientes(n=50)
    ruta_clientes = os.path.join(OUTPUT_DIR, "clientes.csv")
    df_clientes.to_csv(ruta_clientes, index=False, encoding="utf-8")
    print(f"      ✔ Guardado en: {ruta_clientes}")
    print(df_clientes.head(3).to_string(index=False))

    # 2. Versiones de software
    print("\n[2/3] Generando DataFrame de versiones_software (8 registros)...")
    df_versiones = generar_versiones_software()
    ruta_versiones = os.path.join(OUTPUT_DIR, "versiones_software.csv")
    df_versiones.to_csv(ruta_versiones, index=False, encoding="utf-8")
    print(f"      ✔ Guardado en: {ruta_versiones}")
    print(df_versiones.to_string(index=False))

    # 3. Instalaciones
    print("\n[3/3] Generando DataFrame de instalaciones (100 registros)...")
    df_instalaciones = generar_instalaciones(df_clientes, df_versiones, n=100)
    ruta_instalaciones = os.path.join(OUTPUT_DIR, 'instalaciones.csv')
    df_instalaciones.to_csv(ruta_instalaciones, index=False, encoding="utf-8")
    print(f"      ✔ Guardado en: {ruta_instalaciones}")
    print(df_instalaciones.head(3).to_string(index=False))

    # Resumen final
    print("\n" + "=" * 60)
    print("  RESUMEN DE DATOS GENERADOS")
    print("=" * 60)
    print(f"  clientes          : {len(df_clientes)} registros")
    print(f"  versiones_software: {len(df_versiones)} registros")
    print(f"  instalaciones     : {len(df_instalaciones)} registros")

    vuln = df_versiones[df_versiones["contiene_sunburst"] == True]["version_id"].tolist()
    ins_vuln = df_instalaciones[df_instalaciones["version_id"].isin(vuln)]
    print(f"\n  Instalaciones con versión VULNERABLE : {len(ins_vuln)}")
    print(f"  Instalaciones con versión SEGURA     : {len(df_instalaciones) - len(ins_vuln)}")
    print("\n  Archivos CSV generados exitosamente.\n")

    return df_clientes, df_versiones, df_instalaciones


if __name__ == "__main__":
    main()

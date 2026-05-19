

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from faker import Faker

# Inicializamos Faker para simular fechas realistas
fake = Faker()

# ============================================================
# ENTREGABLE 1: CARGAR LOS DATOS DEL ROL 1
# ============================================================
print("--- PASO 1: CARGANDO ARCHIVOS DEL ROL 1 ---")
df_instalaciones = pd.read_csv('data/instalaciones.csv')
df_versiones = pd.read_csv('data/versiones_software.csv')

# Guardamos los IDs válidos en una lista para verificar la calidad más adelante
lista_ids_validos = df_instalaciones['instalacion_id'].tolist()


# ============================================================
# ENTREGABLE 2: GENERAR LA TABLA 4 (eventos_seguridad - 200 registros)
# ============================================================
print("\n--- PASO 2: GENERANDO DATAFRAME 4 (eventos_seguridad) ---")
# Fijamos la semilla para reproducibilidad (requisito de la guía)
np.random.seed(42)

# Listas vacías para ir llenando con un ciclo for tradicional
ids_eventos = []
ids_instalaciones = []
fechas = []
tipos = []
severidades = []

# Catálogos del problema
opciones_eventos = ['Tráfico de Red Anómalo', 'Acceso no Autorizado', 'Actualización Sistema', 'Ping de Rutina']
opciones_severidad = ['Baja', 'Media', 'Alta', 'Crítica']

for i in range(1, 201):
    # Generamos IDs secuenciales: EVT-0001, EVT-0002...
    ids_eventos.append("EVT-" + str(i).zfill(4))

    # INTRODUCIR IMPUREZAS INTENCIONALES (Para evaluar la Integridad Referencial)
    # A los primeros 5 registros les asignamos un ID falso que no existe en la tabla del Rol 1
    if i <= 5:
        ids_instalaciones.append("INST-9999")
    else:
        ids_instalaciones.append(np.random.choice(lista_ids_validos))

    # Fechas realistas dentro del rango del ataque (Año 2020) usando Faker
    fechas.append(fake.date_between_dates(date_start=pd.to_datetime('2020-01-01'), date_end=pd.to_datetime('2020-12-31')))

    # Asignamos eventos y severidades de forma aleatoria
    tipos.append(np.random.choice(opciones_eventos))
    severidades.append(np.random.choice(opciones_severidad))

# Construimos el DataFrame inicial
df_eventos = pd.DataFrame({
    'evento_id': ids_eventos,
    'instalacion_id': ids_instalaciones,
    'timestamp': fechas,
    'tipo_evento': tipos,
    'severidad': severidades
})

# Convert the 'timestamp' column to datetime objects to ensure consistent type for comparisons
df_eventos['timestamp'] = pd.to_datetime(df_eventos['timestamp'])


# ============================================================
# ENTREGABLE 3: DETECCIÓN DE ANOMALÍAS (Caso SUNBURST)
# ============================================================
print("\n--- PASO 3: DETECTANDO CASOS REALES DEL ATAQUE ---")
# Cruzamos los datos con las tablas del Rol 1 para conocer las versiones del software
df_cruce1 = df_eventos.merge(df_instalaciones, on='instalacion_id', how='left')
df_cruce_final = df_cruce1.merge(df_versiones, on='version_id', how='left')

# El patrón del ataque real: Tráfico de Red Anómalo, severidad Alta/Crítica
# y que la versión del software contenga el virus (contiene_sunburst es True)
condicion_ataque = (
    (df_cruce_final['tipo_evento'] == 'Tráfico de Red Anómalo') &
    (df_cruce_final['severidad'].isin(['Alta', 'Crítica'])) &
    (df_cruce_final['contiene_sunburst'] == True)
)

# Creamos la columna requerida: True para ataques reales, False para ruido común o falsos positivos
df_eventos['es_anomalo'] = condicion_ataque


# --- MÁS IMPUREZAS INTENCIONALES (Para evaluar Completitud y Exactitud) ---
df_eventos.loc[10:13, 'tipo_evento'] = None                    # 4 nulos en tipo_evento
df_eventos.loc[50, 'timestamp'] = pd.to_datetime('2035-05-17') # 1 fecha incoherente en el futuro

# Guardamos el archivo final de la Tabla 4
df_eventos.to_csv('data/eventos_seguridad.csv', index=False)
print("¡Archivo 'eventos_seguridad.csv' exportado con éxito!")


# ============================================================
# ENTREGABLE 4: EVALUACIÓN DE CALIDAD DE DATOS (TABLA 5 - MARCO DAMA)
# ============================================================
print("\n--- PASO 4: CALCULANDO REGLAS DE CALIDAD DAMA ---")
total_filas = len(df_eventos)

# 1. Métrica: Completitud (Validación de nulos)
cant_nulos = df_eventos['tipo_evento'].isna().sum()
porc_completitud = ((total_filas - cant_nulos) / total_filas) * 100

# 2. Métrica: Exactitud (Fechas válidas, menores al año actual 2026)
cant_fechas_malas = (df_eventos['timestamp'] > pd.to_datetime('2026-12-31')).sum()
porc_exactitud = ((total_filas - cant_fechas_malas) / total_filas) * 100

# 3. Métrica: Consistencia (Valores dentro del catálogo autorizado de severidad)
cant_sev_malas = 0
for fila in df_eventos['severidad']:
    if fila not in opciones_severidad:
        cant_sev_malas += 1
porc_consistencia = ((total_filas - cant_sev_malas) / total_filas) * 100

# 4. Métrica: Integridad Referencial (Cruce de llaves con instalaciones.csv del Rol 1)
cant_ids_malos = 0
for fila in df_eventos['instalacion_id']:
    if fila not in lista_ids_validos:
        cant_ids_malos += 1
porc_integridad = ((total_filas - cant_ids_malos) / total_filas) * 100

# Estructuramos el DataFrame de la Tabla 5
df_reporte = pd.DataFrame({
    'tabla': ['eventos_seguridad'] * 4,
    'columna': ['tipo_evento', 'timestamp', 'severidad', 'instalacion_id'],
    'metrica': ['Completitud', 'Exactitud', 'Consistencia', 'Integridad Referencial'],
    'valor_actual': [f"{porc_completitud}%", f"{porc_exactitud}%", f"{porc_consistencia}%", f"{porc_integridad}%"],
    'umbral': ['100%'] * 4,
    'estado': [
        'Aprobado' if cant_nulos == 0 else 'Fallo',
        'Aprobado' if cant_fechas_malas == 0 else 'Fallo',
        'Aprobado' if cant_sev_malas == 0 else 'Fallo',
        'Aprobado' if cant_ids_malos == 0 else 'Fallo'
    ]
})

# Guardamos el archivo de la Tabla 5
df_reporte.to_csv('data/reporte_calidad.csv', index=False)
print("¡Archivo 'reporte_calidad.csv' exportado con éxito!")
print(df_reporte)


# ============================================================
# ENTREGABLE 5: VISUALIZACIONES (4 GRÁFICOS PNG CON MATPLOTLIB)
# ============================================================
print("\n--- PASO 5: GENERANDO GRÁFICAS ESTADÍSTICAS ---")

# Gráfico 1: Hipótesis de Prensa vs Evidencia Real (Detección de anomalías)
plt.figure(figsize=(6, 4))
conteos = df_eventos['es_anomalo'].value_counts()
plt.bar(['Falsos Positivos / Alertas', 'Ataques Reales'], [conteos.get(False, 0), conteos.get(True, 0)], color=['blue', 'red'])
plt.title('Caso SUNBURST: Ruido en Alertas vs Ataques Reales')
plt.ylabel('Cantidad de Eventos')
plt.savefig('visualizations/grafico1_sunburst_realidad.png')
plt.close()

# Gráfico 2: Distribución por Tipo de Evento
plt.figure(figsize=(6, 4))
conteo_tipos = df_eventos['tipo_evento'].value_counts()
plt.bar(conteo_tipos.index, conteo_tipos.values, color='green')
plt.title('Frecuencia por Tipo de Evento')
plt.xticks(rotation=15)
plt.savefig('visualizations/grafico2_tipos_eventos.png')
plt.close()

# Gráfico 3: Severidad de las anomalías reales encontradas
plt.figure(figsize=(5, 4))
df_solo_anomalo = df_eventos[df_eventos['es_anomalo'] == True]
conteo_sev = df_solo_anomalo['severidad'].value_counts()
plt.bar(conteo_sev.index, conteo_sev.values, color='orange')
plt.title('Severidad en Eventos de Ataque Confirmados')
plt.savefig('visualizations/grafico3_severidad_ataques.png')
plt.close()

# Gráfico 4: Cuadro de Mando - Calidad de Datos DAMA
plt.figure(figsize=(6, 4))
nombres_metricas = ['Completitud', 'Exactitud', 'Consistencia', 'Integridad']
valores_metricas = [porc_completitud, porc_exactitud, porc_consistencia, porc_integridad]
plt.bar(nombres_metricas, valores_metricas, color='purple')
plt.axhline(100, color='black', linestyle='--', alpha=0.5, label='Umbral (100%)')
plt.ylim(80, 105)
plt.title('Resultados de Control de Calidad (DAMA)')
plt.ylabel('Porcentaje %')
plt.legend()
plt.savefig('visualizations/grafico4_reporte_calidad.png')
plt.close()

print("\n--- ¡PROCESO CONCLUIDO CON ÉXITO! ")
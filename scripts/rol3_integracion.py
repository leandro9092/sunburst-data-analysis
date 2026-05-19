
# ROL 3 - INTEGRADOR DE DATOS

# Importo las librerías que voy a necesitar
import pandas as pd           # para trabajar con tablas de datos
import numpy as np            # para operaciones numéricas
import matplotlib.pyplot as plt  # para hacer las gráficas
import matplotlib.gridspec as gridspec  # para organizar varias gráficas juntas
import warnings
warnings.filterwarnings('ignore')  # para que no salgan advertencias molestas

# ============================================================
# PASO 1: CARGAR LOS ARCHIVOS CSV
# Aquí cargo todos los archivos que generaron el Rol 1 y Rol 2
# ============================================================
print("PASO 1: Cargando los archivos CSV...")

# --- Archivos del Rol 1 ---
clientes      = pd.read_csv('data/clientes.csv')
versiones     = pd.read_csv('data/versiones_software.csv')
instalaciones = pd.read_csv('data/instalaciones.csv')

# --- Archivos del Rol 2 ---
eventos       = pd.read_csv('data/eventos_seguridad.csv')
reporte_cal   = pd.read_csv('data/reporte_calidad.csv')

# Muestro cuántas filas y columnas tiene cada tabla
print(f"  clientes:           {clientes.shape[0]} filas, {clientes.shape[1]} columnas")
print(f"  versiones:          {versiones.shape[0]} filas, {versiones.shape[1]} columnas")
print(f"  instalaciones:      {instalaciones.shape[0]} filas, {instalaciones.shape[1]} columnas")
print(f"  eventos_seguridad:  {eventos.shape[0]} filas, {eventos.shape[1]} columnas")
print(f"  reporte_calidad:    {reporte_cal.shape[0]} filas, {reporte_cal.shape[1]} columnas")

# ============================================================
# PASO 2: LIMPIEZA DE DATOS
# El reporte de calidad del Rol 2 detectó algunos problemas,
# así que los corrijo antes de hacer el merge
# ============================================================
print("\nPASO 2: Limpiando los datos...")

# Problema 1: hay filas donde tipo_evento está vacío (null)
# Las elimino porque no puedo saber qué tipo de evento fue
filas_antes = len(eventos)
eventos = eventos.dropna(subset=['tipo_evento'])
print(f"  Filas con tipo_evento vacío eliminadas: {filas_antes - len(eventos)}")

# Problema 2: hay registros con instalacion_id = 'INST-9999'
# Esa ID no existe en el Rol 1, así que es un dato inválido
mask_invalida = eventos['instalacion_id'] == 'INST-9999'
print(f"  Registros con ID inválida (INST-9999): {mask_invalida.sum()}")
eventos = eventos[~mask_invalida].copy()
print(f"  Total eventos válidos después de limpiar: {len(eventos)}")

# ============================================================
# PASO 3: MERGE - UNIR TODAS LAS TABLAS
# Uso pandas merge() para relacionar los DataFrames,
# es como hacer un JOIN en SQL (que vimos en clase)
# ============================================================
print("\nPASO 3: Uniendo tablas con merge()...")

# Primero uno instalaciones con versiones para saber si cada
# instalación tiene SUNBURST o no
df = pd.merge(
    instalaciones,
    versiones[['version_id', 'nombre_version', 'contiene_sunburst']],
    on='version_id',   # columna que tienen en común
    how='left'         # left join: me quedo con todas las instalaciones
)

# Luego agrego la información de los clientes
df = pd.merge(
    df,
    clientes,
    on='cliente_id',
    how='left'
)

# Ahora proceso los eventos: quiero saber por instalación
# cuántos eventos tuvo, cuántos fueron anómalos, etc.
eventos_por_instalacion = eventos.groupby('instalacion_id').agg(
    total_eventos       = ('evento_id',   'count'),
    eventos_anomalos    = ('es_anomalo',  'sum'),
    tiene_critico       = ('severidad',   lambda x: (x == 'Crítica').any()),
    tiene_acceso_no_auth= ('tipo_evento', lambda x: (x == 'Acceso no Autorizado').any()),
    primera_fecha       = ('timestamp',   'min'),
    ultima_fecha        = ('timestamp',   'max')
).reset_index()

# Uno el resultado con los eventos agregados
df = pd.merge(df, eventos_por_instalacion, on='instalacion_id', how='left')

# Relleno con 0 donde no hay eventos (instalaciones sin actividad registrada)
df['total_eventos']     = df['total_eventos'].fillna(0)
df['eventos_anomalos']  = df['eventos_anomalos'].fillna(0)

print(f"  DataFrame consolidado: {df.shape[0]} filas, {df.shape[1]} columnas")
print(f"  Columnas: {list(df.columns)}")

# ============================================================
# PASO 4: CLASIFICAR CLIENTES
# Identifico cuáles instalaciones fueron solo expuestas
# y cuáles quedaron realmente comprometidas
# ============================================================
print("\nPASO 4: Clasificando expuestos vs comprometidos...")

# EXPUESTO = instaló una versión que tiene SUNBURST (VER-001 a VER-005)
df['expuesto'] = df['contiene_sunburst'] == True

# COMPROMETIDO = expuesto + además tuvo actividad sospechosa real
# (eventos anómalos, acceso no autorizado, o alertas críticas)
df['comprometido'] = (
    df['expuesto'] &
    (
        (df['eventos_anomalos'] > 0) |
        (df['tiene_acceso_no_auth'] == True) |
        (df['tiene_critico'] == True)
    )
)

# Muestro el resumen
total           = len(df)
expuestos       = int(df['expuesto'].sum())
comprometidos   = int(df['comprometido'].sum())
no_afectados    = total - expuestos

print(f"  Total instalaciones:    {total}")
print(f"  No afectadas:           {no_afectados}")
print(f"  Solo expuestas:         {expuestos - comprometidos}")
print(f"  Comprometidas:          {comprometidos}")

# ============================================================
# PASO 5: DATAFRAME 6 - eventos_ciclo_vida
# Mapeo cada evento a una fase del ciclo de vida DAMA DMBOK
# ============================================================
print("\nPASO 5: Creando DataFrame 6 - eventos_ciclo_vida...")

# Diccionario que mapea cada tipo de evento a su fase DAMA
# Lo hago así porque es la forma más clara de verlo
MAPA_FASE = {
    'Actualización Sistema':   'Mantenimiento',
    'Tráfico de Red Anómalo':  'Uso',
    'Ping de Rutina':          'Uso',
    'Acceso no Autorizado':    'Eliminación',
}

# Diccionario que mapea cada fase a su área oficial en DAMA DMBOK
MAPA_AREA_DAMA = {
    'Planificación':  'Data Strategy & Architecture',
    'Creación':       'Data Modeling & Design',
    'Mantenimiento':  'Data Storage & Operations',
    'Uso':            'Data Security & Privacy',
    'Archivo':        'Reference & Master Data',
    'Eliminación':    'Document & Content Management',
}

# Asigno la fase a cada evento
# Si el tipo de evento no está en el diccionario, lo pongo en 'Planificación'
eventos['fase_ciclo_vida'] = eventos['tipo_evento'].map(MAPA_FASE).fillna('Planificación')
eventos['area_dama']       = eventos['fase_ciclo_vida'].map(MAPA_AREA_DAMA)

# Construyo el DataFrame 6 con las columnas que pide el enunciado
df_eventos_ciclo_vida = pd.DataFrame({
    'evento_id':       eventos['evento_id'].values,
    'fase_ciclo_vida': eventos['fase_ciclo_vida'].values,
    'fecha':           eventos['timestamp'].values,
    'descripcion':     eventos['tipo_evento'].values,
    'area_dama':       eventos['area_dama'].values,
})

# Guardo el CSV
df_eventos_ciclo_vida.to_csv('data/eventos_ciclo_vida.csv', index=False)
print(f"  eventos_ciclo_vida.csv guardado: {df_eventos_ciclo_vida.shape[0]} filas")
print(f"  Distribución por fase:")
print(df_eventos_ciclo_vida['fase_ciclo_vida'].value_counts().to_string())

# ============================================================
# PASO 6: DATAFRAME 7 - resumen_impacto
# Tabla resumen con el impacto por versión de software
# ============================================================
print("\nPASO 6: Creando DataFrame 7 - resumen_impacto...")

# Calculo las métricas para cada versión
filas_resumen = []
for ver in versiones['version_id']:
    sub = df[df['version_id'] == ver]
    filas_resumen.append({
        'version_id':             ver,
        'total_instalaciones':    len(sub),
        'clientes_expuestos':     int(sub['expuesto'].sum()),
        'clientes_comprometidos': int(sub['comprometido'].sum()),
    })

df_resumen_impacto = pd.DataFrame(filas_resumen)
df_resumen_impacto.to_csv('data/resumen_impacto.csv', index=False)
print(f"  resumen_impacto.csv guardado")
print(df_resumen_impacto.to_string(index=False))

# ============================================================
# PASO 7: MÉTRICAS POR FASE
# Calculo cuántos eventos hay en cada fase del ciclo de vida
# ============================================================
print("\nPASO 7: Métricas por fase del ciclo de vida...")

metricas = df_eventos_ciclo_vida.groupby('fase_ciclo_vida').agg(
    total_eventos = ('evento_id', 'count'),
    area_dama     = ('area_dama', 'first')
).reset_index().sort_values('total_eventos', ascending=False)

print(metricas.to_string(index=False))

# ============================================================
# PASO 8: VISUALIZACIONES - DASHBOARD
# Creo 4 gráficos y los junto en un solo dashboard PNG
# ============================================================
print("\nPASO 8: Generando el dashboard con las visualizaciones...")

# Defino los colores que voy a usar en todas las gráficas
COLOR_FONDO    = '#1A1A2E'
COLOR_TEXTO    = '#FFFFFF'
COLOR_GRID     = '#333355'
COLOR_ROJO     = '#E63946'
COLOR_VERDE    = '#2A9D8F'
COLOR_NARANJA  = '#F4A261'
COLOR_AMARILLO = '#E9C46A'

# Creo una figura con 4 subgráficos (2 filas x 2 columnas)
fig = plt.figure(figsize=(20, 14), facecolor=COLOR_FONDO)
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.38)

# --- Gráfico 1: Timeline del ataque (eventos por mes) ---
ax1 = fig.add_subplot(gs[0, 0])
eventos['timestamp'] = pd.to_datetime(eventos['timestamp'])
timeline = eventos.groupby(eventos['timestamp'].dt.to_period('M')).size()
timeline.index = timeline.index.astype(str)
ax1.fill_between(range(len(timeline)), timeline.values, alpha=0.35, color=COLOR_ROJO)
ax1.plot(range(len(timeline)), timeline.values,
         color=COLOR_ROJO, linewidth=2.5, marker='o', markersize=5)
# Marco el mes con más eventos
pico = int(np.argmax(timeline.values))
ax1.annotate(f'Pico: {timeline.values[pico]} eventos',
             xy=(pico, timeline.values[pico]),
             xytext=(pico + 0.5, timeline.values[pico] + 1),
             color=COLOR_AMARILLO, fontsize=9, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=COLOR_AMARILLO))
ax1.set_facecolor(COLOR_FONDO)
ax1.set_title('Timeline del Ataque SUNBURST\n(Eventos por Mes)',
              color=COLOR_TEXTO, fontsize=13, fontweight='bold')
ax1.set_xticks(range(len(timeline)))
ax1.set_xticklabels(timeline.index, rotation=45, ha='right', color=COLOR_TEXTO, fontsize=8)
ax1.tick_params(colors=COLOR_TEXTO)
ax1.spines[:].set_color(COLOR_GRID)
ax1.set_ylabel('Nº de Eventos', color=COLOR_TEXTO)
ax1.grid(axis='y', color=COLOR_GRID, alpha=0.5)

# --- Gráfico 2: Cascada 18,000 → comprometidos ---
ax2 = fig.add_subplot(gs[0, 1])
etiquetas = ['Clientes\nglobales\nSolarWinds', 'Con versión\nSUNBURST\n(estimado)',
             'Expuestos\n(muestra)', 'Comprometidos\n(muestra)']
valores   = [18000, 8800, expuestos, comprometidos]
colores_c = ['#264653', COLOR_AMARILLO, COLOR_NARANJA, COLOR_ROJO]
barras = ax2.bar(etiquetas, valores, color=colores_c, edgecolor='white', linewidth=1.2, width=0.6)
for barra, val in zip(barras, valores):
    ax2.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 150,
             f'{val:,}', ha='center', va='bottom',
             color=COLOR_TEXTO, fontsize=13, fontweight='bold')
ax2.set_facecolor(COLOR_FONDO)
ax2.set_title('Cascada de Impacto\n18,000 → Clientes Comprometidos',
              color=COLOR_TEXTO, fontsize=13, fontweight='bold')
ax2.tick_params(colors=COLOR_TEXTO)
ax2.spines[:].set_color(COLOR_GRID)
ax2.set_ylabel('Número de instalaciones / clientes', color=COLOR_TEXTO)
ax2.set_ylim(0, 21000)
ax2.grid(axis='y', color=COLOR_GRID, alpha=0.5)

# --- Gráfico 3: Eventos por fase DAMA ---
ax3 = fig.add_subplot(gs[1, 0])
ORDEN_FASES  = ['Planificación','Creación','Mantenimiento','Uso','Archivo','Eliminación']
COLORES_FASE = ['#264653','#2A9D8F','#E9C46A','#F4A261','#E76F51','#E63946']
fases_count  = df_eventos_ciclo_vida['fase_ciclo_vida'].value_counts()\
               .reindex(ORDEN_FASES, fill_value=0)
barras3 = ax3.barh(ORDEN_FASES, fases_count.values,
                   color=COLORES_FASE, edgecolor='white', linewidth=0.8)
for barra, val in zip(barras3, fases_count.values):
    ax3.text(val + 0.3, barra.get_y() + barra.get_height() / 2,
             str(val), va='center', color=COLOR_TEXTO, fontsize=11, fontweight='bold')
ax3.set_facecolor(COLOR_FONDO)
ax3.set_title('Eventos por Fase del Ciclo de Vida\n(DAMA DMBOK)',
              color=COLOR_TEXTO, fontsize=13, fontweight='bold')
ax3.tick_params(colors=COLOR_TEXTO)
ax3.spines[:].set_color(COLOR_GRID)
ax3.set_xlabel('Número de Eventos', color=COLOR_TEXTO)
ax3.grid(axis='x', color=COLOR_GRID, alpha=0.5)
ax3.invert_yaxis()

# --- Gráfico 4: Tipos de evento por severidad ---
ax4 = fig.add_subplot(gs[1, 1])
tabla_pivot = eventos.groupby(['tipo_evento', 'severidad']).size().unstack(fill_value=0)
orden_sev   = ['Baja', 'Media', 'Alta', 'Crítica']
col_sev     = [COLOR_VERDE, COLOR_AMARILLO, COLOR_NARANJA, COLOR_ROJO]
tabla_pivot = tabla_pivot.reindex(
    columns=[s for s in orden_sev if s in tabla_pivot.columns])
base = np.zeros(len(tabla_pivot))
for sev, color in zip(tabla_pivot.columns, col_sev[:len(tabla_pivot.columns)]):
    ax4.barh(tabla_pivot.index, tabla_pivot[sev], left=base,
             color=color, label=sev, edgecolor='white', linewidth=0.5)
    base += tabla_pivot[sev].values
ax4.set_facecolor(COLOR_FONDO)
ax4.set_title('Tipos de Evento por Severidad\n(Datos reales Rol 2)',
              color=COLOR_TEXTO, fontsize=13, fontweight='bold')
ax4.tick_params(colors=COLOR_TEXTO)
ax4.spines[:].set_color(COLOR_GRID)
ax4.set_xlabel('Número de Eventos', color=COLOR_TEXTO)
ax4.legend(facecolor=COLOR_FONDO, labelcolor=COLOR_TEXTO,
           title='Severidad', title_fontsize=9)
ax4.grid(axis='x', color=COLOR_GRID, alpha=0.5)

# Título general del dashboard
fig.suptitle('DASHBOARD INTEGRADO — ANÁLISIS SUNBURST\nRol 3: Integrador de Datos | DAMA DMBOK',
             color=COLOR_TEXTO, fontsize=16, fontweight='bold', y=0.98)

# Guardo el dashboard como imagen PNG
plt.savefig('visualizations/dashboard_sunburst.png', dpi=150, bbox_inches='tight', facecolor=COLOR_FONDO)
plt.close()
print("  dashboard_sunburst.png guardado correctamente")

print("\n" + "=" * 50)
print("LISTO - Todos los archivos fueron generados:")
print("  eventos_ciclo_vida.csv")
print("  resumen_impacto.csv")
print("  dashboard_sunburst.png")
print("=" * 50)

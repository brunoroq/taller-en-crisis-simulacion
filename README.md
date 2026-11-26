# Taller en Crisis

Simulación de eventos discretos de un taller automotriz para el Trabajo 2 de INFB8091, Universidad Tecnológica Metropolitana, segundo semestre de 2026. Equipo **Kernel en Crisis**.

El taller recibe vehículos de tres clases. Cada vehículo pasa por recepción, diagnóstico, reparación y control de calidad. Tres mecánicos comparten una cola FIFO en reparación. Un rechazo de calidad devuelve el vehículo a esa cola. Los talleres simulados abren vacíos y terminan los trabajos pendientes después del cierre.

## Ejecutar en Windows

Con Python 3.12 disponible en `PATH`, desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe main.py
```

En Linux y macOS, sustituye `.\.venv\Scripts\python.exe` por `.venv/bin/python`. La corrida publicada usa Python 3.12.14 y Ciw 3.2.7. Si el entorno restringe la carpeta de usuario, configura `MPLCONFIGDIR` con un directorio temporal de escritura.

`main.py` ejecuta 100 jornadas por configuración con la semilla maestra `80912026`. `--replicas` acepta un mínimo de 50, `--semilla` permite repetir el diseño con otra semilla, `--salida` dirige `results/` y `figures/` a otra ubicación y `--sin-economia` omite los indicadores en pesos y su gráfico. Los valores operacionales y económicos se editan en [`src/config.py`](src/config.py).

## Experimentos y resultados

| Escenario | Cambio |
| --- | --- |
| E0 | Configuración base |
| E1 | Multiplicadores de demanda 0,50, 0,75, 1,00, 1,25, 1,50, 1,75 y 2,00 |
| E2 | Cuarto mecánico |
| E3 | Probabilidad de retrabajo de 5 % a 2 % |
| E4 | Llegadas Poisson a tasa constante de 2 vehículos/h, con igual demanda esperada |
| E5 | Cuarto mecánico y retrabajo de 2 %, seleccionados en un piloto independiente |

En E0 se entregaron **12,08 vehículos por jornada**, quedaron **3,79 pendientes** y el vaciado tomó **110,0 minutos extra** en promedio. Reparación tuvo la mayor espera por visita y utilización regular. E5 redujo la permanencia media en **12,32 minutos** frente a E0. Con los costos ilustrativos, E3 tiene el mejor balance entre espera, horas extra y costo. El intervalo de confianza de su cambio en margen incluye cero. Consulta el [análisis de resultados](docs/resultados.md) para ver los intervalos, las condiciones de capacidad y los criterios de comparación.

## Archivos

- `src/` y `main.py` contienen la red Ciw, los indicadores, los experimentos y los gráficos. `tests/` comprueba el recorrido, los balances y los cálculos.
- [`docs/modelo.md`](docs/modelo.md) define la red, las ventanas, las cohortes y los estadísticos. [`docs/parametros.md`](docs/parametros.md) explica los supuestos y el cálculo económico.
- [`results/replicas.csv`](results/replicas.csv) y [`results/replicas_estaciones.csv`](results/replicas_estaciones.csv) contienen una fila por jornada y por jornada-estación, respectivamente.
- [`results/resumen.csv`](results/resumen.csv) y [`results/resumen_estaciones.csv`](results/resumen_estaciones.csv) contienen el número de observaciones, media, desviación estándar muestral e IC del 95 % por indicador. [`results/diferencias_pareadas_vs_E0.csv`](results/diferencias_pareadas_vs_E0.csv) contiene las diferencias diarias pareadas, y [`results/capacidad_nominal.csv`](results/capacidad_nominal.csv) contiene los balances teóricos de carga.
- [`results/configuracion_ejecutada.json`](results/configuracion_ejecutada.json) registra versiones, supuestos, escenarios y semilla maestra. [`figures/`](figures/) contiene siete gráficos en español. [`prompts/001_desarrollo_inicial.md`](prompts/001_desarrollo_inicial.md) conserva el encargo original.

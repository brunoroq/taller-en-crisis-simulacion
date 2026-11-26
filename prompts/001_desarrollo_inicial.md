# Proyecto: Taller en Crisis — Simulación de redes de colas

## Contexto académico

Estamos desarrollando el Trabajo 2 de la asignatura INFB8091 - Desempeño de Sistemas de la Universidad Tecnológica Metropolitana (UTEM), segundo semestre de 2026.

Equipo: Kernel en Crisis.

El proyecto consiste en modelar y simular un taller mecánico automotriz convencional mediante Python y la biblioteca Ciw.

El nombre Taller en Crisis hace referencia a un proyecto universitario anterior del equipo, pero la simulación debe ser independiente del videojuego y representar un negocio realista.

## Objetivo

Construir una simulación reproducible de eventos discretos que permita evaluar el desempeño operacional del taller, identificar cuellos de botella, determinar límites de capacidad y comparar propuestas de mejora.

Priorizar simplicidad, claridad, rigor académico y rapidez de implementación. No desarrollar funcionalidades innecesarias.

## Requisitos académicos obligatorios

- Modelar un proceso real mediante una red de colas.
- Incorporar al menos dos colas en serie.
- Incorporar una estación con al menos tres servidores paralelos.
- Utilizar obligatoriamente la biblioteca Ciw.
- Construir un modelo que no pueda resolverse fácilmente mediante las fórmulas elementales de teoría de colas.
- Definir y justificar los parámetros de entrada.
- Obtener indicadores de desempeño mediante simulación.
- Realizar pruebas de carga para determinar límites de capacidad.
- Proponer mejoras y volver a simular.
- Exportar fuentes, resultados y gráficos.
- Registrar los prompts utilizados.
- Considerar la factibilidad económica de las mejoras.

## Modelo conceptual

Red abierta de cuatro nodos:

1. Recepción: un servidor.
2. Diagnóstico: un servidor.
3. Reparación: tres mecánicos polivalentes que comparten una única cola.
4. Control de calidad: un servidor.

Flujo:

Llegada → Recepción → Diagnóstico → Reparación → Control de calidad → Salida.

Si el vehículo no supera el control de calidad, regresa a reparación antes de ser entregado al cliente.

La disciplina inicial de atención es FIFO.

Configuración inicial de servidores: [1, 1, 3, 1].

## Clases de clientes

- Neumáticos: 35%.
- Sistema eléctrico: 30%.
- Mecánica general: 35%.

Las clases representan el tipo de falla del vehículo. Todos los mecánicos pueden realizar cualquiera de las tres categorías de reparación.

Mantener la clase del vehículo durante todo su recorrido.

## Parámetros iniciales

Utilizar minutos como unidad de tiempo.

Distribuciones triangulares expresadas como mínimo, moda y máximo:

- Recepción: (3, 5, 7).
- Diagnóstico: (10, 15, 20).
- Reparación de neumáticos: (15, 30, 45).
- Reparación eléctrica: (30, 60, 90).
- Mecánica general: (60, 90, 150).
- Control de calidad: (5, 10, 15).

Probabilidad inicial de retrabajo: 5% después de cada control de calidad.

El retrabajo debe volver a la estación de reparación, conservando la clase del vehículo. Inicialmente utilizar la misma distribución de reparación y documentar que esto constituye una simplificación.

Todos los parámetros son supuestos preliminares, no datos empíricos. Deben centralizarse en la configuración para poder modificarlos fácilmente.

## Llegadas y jornada laboral

Utilizar llegadas Poisson con tasas variables por período de la jornada:

- 09:00 a 11:00: 3 vehículos por hora.
- 11:00 a 15:00: 1,5 vehículos por hora.
- 15:00 a 17:00: 2 vehículos por hora.

La jornada tiene una duración de 480 minutos.

No generar nuevas llegadas después del cierre.

Modelar cada jornada como un sistema inicialmente vacío. Permitir terminar los trabajos pendientes después del cierre, registrando las horas extraordinarias y los vehículos pendientes al minuto 480.

Documentar que este supuesto representa un taller que intenta completar los trabajos recibidos durante la jornada.

Utilizar mecanismos compatibles con la versión instalada de Ciw para implementar correctamente las tasas de llegada variables. No aproximar incorrectamente los cambios de tasa mediante una distribución exponencial que ignore los límites de cada período.

## Indicadores

Obtener mediante los registros y estados de la simulación, tanto globalmente como por estación cuando corresponda:

- Tasa de llegada efectiva.
- Tasa de servicio.
- W o T: tiempo promedio de permanencia.
- Wq o Tq: tiempo promedio de espera.
- L o M: cantidad promedio de vehículos presentes.
- Lq o Mq: cantidad promedio de vehículos esperando.
- Utilización de los servidores.
- Throughput.
- Percentil 95 del tiempo total.
- Vehículos recibidos.
- Vehículos terminados dentro de la jornada.
- Vehículos pendientes al cierre.
- Cantidad de retrabajos.
- Tiempo extraordinario necesario para finalizar los trabajos.

Calcular L y Lq mediante promedios ponderados por tiempo, utilizando los estados o eventos de la simulación.

No calcularlos exclusivamente mediante la ley de Little.

Calcular el tiempo total de cada vehículo considerando todas sus visitas, incluyendo retrabajos.

Distinguir claramente las métricas por visita de las métricas por vehículo.

Definir explícitamente los intervalos de observación. No mezclar indicadores de la jornada regular con los del período de vaciado posterior al cierre.

## Experimentos

Implementar los siguientes escenarios:

E0: escenario base.

E1: análisis de carga, multiplicando las tasas de llegada por factores desde 0,5 hasta 2,0, incluyendo valores intermedios suficientes para observar la saturación.

E2: incorporar un cuarto mecánico.

E3: reducir la probabilidad de retrabajo del 5% al 2%.

E4: distribuir uniformemente las llegadas durante la jornada, manteniendo la misma demanda diaria esperada.

E5: combinar las mejoras que resulten convenientes después del análisis.

Para los experimentos utilizar al menos 50 réplicas independientes por escenario, con semillas reproducibles.

Calcular medias, desviaciones estándar e intervalos de confianza del 95% para los indicadores principales.

Para comparar escenarios utilizar conjuntos de semillas consistentes y documentar sus limitaciones.

En las pruebas de carga analizar utilización, tiempos de espera, trabajos pendientes al cierre y horas extraordinarias. No declarar que un sistema es estable únicamente porque logra vaciarse después de detener las llegadas.

## Dimensión económica

Incorporar un módulo sencillo y configurable que permita estimar:

- Ingresos por reparaciones.
- Costos variables por categoría de reparación.
- Costos diarios de personal.
- Costos operacionales.
- Costos de horas extraordinarias.
- Margen operacional estimado.

No inventar fuentes ni presentar precios hipotéticos como datos reales.

Inicialmente documentar los parámetros económicos como supuestos pendientes de validación.

Evitar desarrollar un sistema contable completo.

## Arquitectura

Crear una estructura sencilla:

- src/config.py
- src/model.py
- src/metrics.py
- src/experiments.py
- src/plots.py
- tests/
- results/
- figures/
- docs/modelo.md
- docs/parametros.md
- prompts/001_desarrollo_inicial.md
- main.py
- README.md
- requirements.txt
- AGENTS.md
- .gitignore

Se permite ajustar esta estructura si existe una justificación técnica, evitando sobreingeniería.

## Resultados y gráficos

Exportar archivos CSV con los resultados individuales y agregados de las réplicas.

Generar gráficos de:

1. Tiempo promedio de espera por estación.
2. Utilización por estación.
3. Tiempo de respuesta frente a la carga.
4. Vehículos pendientes al cierre frente a la carga.
5. Throughput frente a la carga.
6. Comparación de escenarios de mejora.
7. Comparación económica cuando estén definidos los parámetros.

Utilizar títulos, unidades y etiquetas en español.

## Validación

Implementar pruebas automatizadas que comprueben:

- Reproducibilidad con una misma semilla.
- Conservación de vehículos.
- Recorrido correcto por los nodos.
- Funcionamiento de las clases de clientes.
- Funcionamiento de los retrabajos.
- Ausencia de tiempos negativos.
- Utilización dentro de límites válidos.
- Cálculo correcto de indicadores temporales.
- Ausencia de llegadas posteriores al cierre.
- Coherencia entre vehículos terminados y pendientes.

Utilizar las leyes operacionales, incluyendo la ley de Little cuando corresponda y se cumplan sus condiciones, como comprobaciones adicionales, no como sustituto de la simulación.

## Instrucciones de ejecución

1. Inspecciona primero el repositorio y el entorno.
2. Crea AGENTS.md con las instrucciones permanentes del proyecto.
3. Guarda este prompt en prompts/001_desarrollo_inicial.md.
4. Instala las dependencias necesarias.
5. Verifica la versión y API real de Ciw antes de implementar.
6. Implementa el modelo y las métricas.
7. Ejecuta las pruebas y corrige los errores.
8. Ejecuta los experimentos.
9. Genera los CSV y gráficos.
10. Documenta las instrucciones de ejecución y las decisiones tomadas.

No te limites a entregar ejemplos de código o un plan. Implementa y ejecuta el proyecto en el entorno disponible.

No inventes resultados de simulación, referencias bibliográficas ni mediciones reales.

Si algún requisito presenta dificultades técnicas, documenta el problema y aplica la solución compatible más sencilla, manteniendo el cumplimiento académico.

Al finalizar, presenta un resumen con:

- Archivos creados.
- Decisiones técnicas.
- Pruebas ejecutadas y resultados.
- Indicadores obtenidos.
- Cuellos de botella observados.
- Limitaciones.
- Supuestos pendientes de validación.
- Recomendaciones para la siguiente iteración.
# Fase 2 — Auditoría académica y técnica

Revisa exhaustivamente la implementación actual de Taller en Crisis, sin agregar funcionalidades innecesarias ni modificar todavía los parámetros del escenario base.



El objetivo es verificar que los resultados sean correctos, reproducibles y defendibles frente al profesor de Desempeño de Sistemas.

## 1. Auditoría del modelo

Verifica:

- Que la simulación utiliza efectivamente Ciw.
- Que existen cuatro nodos en serie con configuración [1, 1, 3, 1].
- Que los tres mecánicos comparten una cola.
- Que las clases de reparación conservan sus características durante todo el recorrido.
- Que las distribuciones triangulares utilizan correctamente mínimo, moda y máximo.
- Que las llegadas por períodos horarios están correctamente implementadas.
- Que los retrabajos no se contabilizan como nuevos clientes.
- Que los vehículos pendientes al cierre se contabilizan correctamente.

## 2. Auditoría de indicadores

Genera una tabla consolidada del escenario base con:

- Estación.
- Número de servidores.
- Tasa de llegada efectiva.
- Tiempo medio de servicio.
- Tasa de servicio por servidor.
- W.
- Wq.
- L.
- Lq.
- Utilización.
- Throughput.

Genera también los indicadores globales.



Especifica las unidades, los intervalos de observación y si cada indicador se calcula por visita o por vehículo.



Verifica los cálculos directamente contra los registros y estados de la simulación.



Comprueba la ley de Little únicamente cuando las condiciones y los intervalos de medición sean compatibles.

## 3. Interpretación de resultados

Investiga por qué el taller necesita 110 minutos adicionales de vaciado si la utilización promedio de reparación es del 60,8%.



Determina qué parte del problema se relaciona con:

- Congestión.
- Llegadas cercanas al cierre.
- Duración de las reparaciones.
- Retrabajos.

Distingue entre hipótesis y resultados respaldados por los registros.



Aclara la diferencia entre capacidad nominal, saturación y límite operativo definido por metas de servicio.

## 4. Auditoría económica

Presenta todos los parámetros económicos utilizados actualmente, incluyendo ingresos, costos variables, remuneraciones, costos operacionales y horas extraordinarias.



Identifica cuáles son supuestos y cuáles tienen respaldo documental.



Comprueba que los ingresos y costos correspondan al mismo conjunto de vehículos y horizonte temporal.



Verifica que el costo de horas extraordinarias se relacione correctamente con los recursos que efectivamente trabajan después del cierre.

## 5. Entregables

Crea docs/auditoria.md con los hallazgos.



Crea docs/resumen_academico.md con:

- Problemática.
- Modelo conceptual.
- Parámetros de entrada.
- Indicadores obtenidos.
- Tabla comparativa de todos los escenarios.
- Interpretación de resultados.
- Justificación de las mejoras.
- Limitaciones.
- Cumplimiento de los requisitos académicos.

Guarda este prompt en prompts/002_auditoria.md.



No inventes fuentes ni resultados.



No cambies el modelo sin justificarlo. Si encuentras errores, documenta primero su naturaleza, impacto y propuesta de corrección.



Al finalizar, informa los hallazgos, las inconsistencias detectadas y las decisiones que requieren revisión humana.

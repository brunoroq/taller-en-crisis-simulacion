# Modelo y medición

## Red y límites del sistema

**Llegada → Recepción (1) → Diagnóstico (1) → Reparación (3) → Control de calidad (1) → Entrega.** Un vehículo rechazado en calidad retorna al final de la cola única de reparación y vuelve a pasar por calidad. Su clase se conserva. Todas las estaciones usan FIFO, los mecánicos son polivalentes y las colas tienen capacidad ilimitada. El modelo carece de prioridades, pausas, abandono, limitaciones de repuestos y restricciones físicas de estacionamiento.

La jornada comienza vacía a las 09:00 y recibe vehículos hasta las 17:00. Después del cierre, los mismos servidores terminan el trabajo pendiente. La siguiente réplica corresponde a otra jornada inicialmente vacía. El modelo representa un taller que intenta finalizar todo lo recibido el mismo día, incluso si necesita horas extra.

La combinación de tasas de entrada variables, servicios triangulares con mezcla de clases, realimentación y un horizonte transitorio hace que las fórmulas elementales de colas estacionarias sean insuficientes para obtener los indicadores solicitados.

## Implementación en Ciw 3.2.7

Se generan puntos de un Poisson homogéneo unitario en el reloj de intensidad acumulada. Para un punto `x` en un tramo que empieza en `a` con intensidad acumulada `A` y tasa por minuto `r`, su llegada ocurre en `a + (x − A) / r`. Si `x` cae más allá del tramo, se conserva el mismo punto y se evalúa con la intensidad y tasa del tramo siguiente. El proceso termina cuando el próximo punto alcanza la intensidad del cierre. Cada llegada se marca independientemente con su clase.

La distribución finita `ScheduledArrivals`, derivada de `ciw.dists.Distribution`, entrega a Ciw las diferencias entre llegadas consecutivas de cada clase y devuelve infinito al agotarlas. `None` desactiva las llegadas externas en las otras estaciones. Ciw ejecuta FIFO, muestrea `Triangular(lower, mode, upper)`, enruta cada clase con `TransitionMatrix` y simula hasta que el número planificado de vehículos completa el recorrido. La salida de calidad tiene probabilidad `1 − p`. El tiempo extraordinario transcurrido es `max(0, última entrega − 480)`. [API de distribuciones](https://ciw.readthedocs.io/en/latest/Reference/distributions.html) · [Matrices en Ciw](https://ciw.readthedocs.io/en/latest/Guides/Routing/transition_matrix.html)

## Ventanas y cohortes

| Nombre en los CSV | Definición |
| --- | --- |
| `jornada` | Minutos 0 a 480. Se aceptan llegadas externas antes de 480 y se cuentan las salidas ocurridas hasta 480 inclusive. |
| `vaciado` | Después de 480 y hasta la última entrega. Las llegadas externas son cero. Puede haber entradas internas a estaciones, incluidas las de retrabajo. |
| `cohorte` | Vehículos recibidos durante la jornada y seguidos hasta su entrega. Incluye todas sus visitas, aunque alguna termine dentro del vaciado. |
| `terminado_jornada` o `terminada_jornada` | Vehículos entregados o visitas finalizadas hasta el minuto 480, según la unidad del indicador. Es un subconjunto que puede favorecer servicios más rápidos. |

## Indicadores y unidades

- **λ y throughput.** Entradas y salidas por hora de cada ventana. En la red son vehículos externos y entregas finales. En cada estación son visitas, incluidas las repetidas. `throughput_cohorte_h` divide las entregas por las horas desde apertura hasta `max(480, última entrega)`.
- **μ.** Por estación es 60 dividido por la media de servicio activo por visita, en visitas por servidor-hora. Se calcula con todas las visitas de la cohorte y también para visitas terminadas en jornada. `mu_equivalente_cohorte_por_h_persona` divide vehículos por las horas-persona activas de todas sus visitas. Es una productividad equivalente de trabajo, mientras que la capacidad nominal de una estación considera sus servidores y visitas esperadas.
- **W, Wq y P95.** Para un vehículo, W es el tiempo entre llegada y entrega, y Wq es la suma de sus esperas, incluyendo cada retrabajo. En una visita, W abarca desde entrada hasta salida de la estación y Wq hasta el inicio del servicio. El P95 reportado es el promedio de los P95 calculados por réplica mediante interpolación lineal. W y Wq de la cohorte usan el recorrido completo y pueden extenderse después del cierre.
- **L, Lq y utilización.** Para cada visita se mide la longitud de la intersección de su permanencia, espera y servicio con la ventana. Las sumas de permanencia y espera, divididas por los minutos observados, producen L y Lq. La suma de servicio activo se divide por servidores × minutos de la ventana para producir utilización. La utilización global pondera por servidores. La suma de las ocupaciones de estaciones coincide con la ocupación global porque el traslado es instantáneo.
- **Cierre y retrabajos.** Los recibidos se reparten entre terminados en jornada y pendientes. Los pendientes coinciden con las entregas durante el vaciado. El contador de retrabajos suma cada salida de calidad que retorna a reparación. `extra_min` mide tiempo transcurrido desde el cierre. `minutos_persona_vaciado` mide servicio activo acumulado y permite calcular su costo por estación.

Una ventana sin duración deja vacíos los indicadores que requieren dividir por su longitud. Una réplica sin vehículos o visitas deja vacíos los tiempos de esa cohorte. El agregado incluye el número efectivo `n` por indicador. Las celdas vacías significan que la métrica es indefinida para esa observación.

## Diseño experimental y comprobaciones

La unidad de observación es una jornada independiente. `SeedSequence.spawn` deriva 100 semillas de la semilla maestra 80912026. Cada jornada separa las semillas para tiempos de llegada, marcas de clase y Ciw. Todas las configuraciones reutilizan el conjunto de 100 semillas. E0 y E1 a 1× coinciden exactamente. En E4 se comparte la secuencia de puntos de intensidad y clases de E0, cambiando los minutos de llegada y manteniendo los conteos. En E1 se comparten puntos y clases hasta el nivel de intensidad alcanzado. El orden de eventos puede cambiar qué vehículo consume cada muestra de servicio o enrutamiento de Ciw, por lo que el pareo no sincroniza todos los tiempos individuales.

Para cada métrica se da el promedio diario, la desviación estándar muestral y el intervalo t bilateral del 95 % `media ± t(0,975; n−1) × DE / √n`. Los tiempos diarios ponderan todas las jornadas igualmente. Las comparaciones contra E0 usan las diferencias réplica a réplica y su IC t. Los intervalos son nominales por indicador, sin ajuste por comparaciones múltiples, y reflejan variación de simulación bajo los parámetros fijados.

Las pruebas verifican balances de vehículos, recorrido, rangos de servicio, FIFO, cortes temporales y relaciones de ocupación. Como comprobación adicional, en la observación completa que empieza y termina vacía se verifica `L = (N/H) × W` y `Lq = (N/H) × Wq`, con `H` en minutos y todos los vehículos observados íntegramente. En la jornada de 480 minutos quedan trayectorias truncadas, por lo que esa verificación solo se realiza sobre la observación completa.

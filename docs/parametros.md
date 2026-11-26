# Parámetros y supuestos

Todos los valores operacionales y económicos son supuestos iniciales. El proyecto modela un taller convencional hipotético. Los valores se centralizan en [`src/config.py`](../src/config.py) y quedan registrados para cada corrida en [`results/configuracion_ejecutada.json`](../results/configuracion_ejecutada.json).

## Demanda y servicios

| Horario | Tasa supuesta (veh/h) | Demanda esperada |
| --- | ---: | ---: |
| 09:00–11:00 | 3,0 | 6 |
| 11:00–15:00 | 1,5 | 6 |
| 15:00–17:00 | 2,0 | 4 |
| Jornada de 8 horas | 2,0 en promedio | 16 |

El perfil representa una concentración de ingresos a primera hora, una baja al mediodía y un repunte hacia el final. Cada período tiene una tasa por hora. Multiplicar todas las tasas preserva la forma del perfil en la prueba de carga. La alternativa uniforme usa `16 / 8 = 2` veh/h durante toda la jornada.

| Operación | Clase o mezcla de llegadas | Triangular (mín., moda, máx.) | Media (min) |
| --- | --- | --- | ---: |
| Recepción | Todas | (3, 5, 7) | 5 |
| Diagnóstico | Todas | (10, 15, 20) | 15 |
| Reparación | Neumáticos, 35 % | (15, 30, 45) | 30 |
| Reparación | Sistema eléctrico, 30 % | (30, 60, 90) | 60 |
| Reparación | Mecánica general, 35 % | (60, 90, 150) | 100 |
| Control de calidad | Todas | (5, 10, 15) | 10 |

Los mínimos representan trabajos rutinarios de baja complejidad y las modas se usan como tiempos típicos. Recepción y control tienen rangos acotados por tratarse de registro y verificaciones. El diagnóstico dura más por la inspección previa. La reparación de neumáticos tiene menor duración y dispersión que la eléctrica o mecánica. La mecánica general admite una cola derecha más larga para representar desmontajes y ajustes variables. La mezcla propone una fracción ligeramente mayor de neumáticos y mecánica general. Las proporciones, los rangos y las modas requieren datos del taller para calibrarse.

Se supone que cada control falla de manera independiente con probabilidad de 5 % en el escenario base y 2 % en E3/E5. El número medio de visitas a reparación y calidad por vehículo es `1/(1 − p)`. En el retrabajo se vuelve a muestrear la misma triangular de reparación de la clase. Es una simplificación que puede sobreestimar el tiempo de una corrección menor o subestimar fallas complejas.

## Economía ilustrativa en CLP

| Categoría | Precio por trabajo | Costo variable por primera reparación |
| --- | ---: | ---: |
| Neumáticos | 50.000 | 18.000 |
| Sistema eléctrico | 100.000 | 32.000 |
| Mecánica general | 170.000 | 65.000 |

| Estación | Costo por persona y jornada | Costo por hora activa extra |
| --- | ---: | ---: |
| Recepción | 30.000 | 6.000 |
| Diagnóstico | 43.000 | 8.000 |
| Reparación | 48.000 | 9.000 |
| Control de calidad | 38.000 | 7.000 |

- Se imputa un costo operacional fijo de 70.000 CLP/día. La mejora de calidad agrega 5.000 CLP/día y la gestión de agenda 3.000 CLP/día. El cuarto mecánico agrega su costo regular de 48.000 CLP/día. No se presupone equipo adicional para habilitar su puesto.
- Cada vehículo genera un ingreso al ser entregado, asignado al día en que ingresó aunque se entregue en el vaciado. Cada visita de retrabajo agrega materiales valorizados al 35 % del costo variable de la clase, sin cobro adicional al cliente.
- El costo extraordinario se obtiene al multiplicar los minutos-persona activos después del cierre por las tarifas horarias respectivas, divididas por 60. Puede quedar por debajo del costo real si el personal debe permanecer disponible mientras espera trabajo.
- El margen operacional es ingresos menos materiales, personal regular, operación, costo incremental de mejoras y horas extraordinarias activas. Los supuestos deben validarse con cotizaciones, remuneraciones, gastos y política de horas extra. La evaluación excluye impuestos, inversión, depreciación y valor económico de mejorar la entrega dentro del turno.

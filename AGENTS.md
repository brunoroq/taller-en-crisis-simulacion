# Taller en Crisis · Kernel en Crisis

- Mantén el simulador reproducible con Ciw y Python 3.12. Ejecuta `python -m unittest discover -s tests -v` y `python main.py` antes de actualizar los resultados.
- Centraliza los supuestos del taller y su economía en `src/config.py`. Distingue datos observados, supuestos y salidas simuladas en la documentación.
- Conserva la clase del vehículo, el retrabajo y la disciplina FIFO según el modelo. Calcula ocupaciones integrando los intervalos de los registros de Ciw.
- Documenta las cohortes, ventanas, unidades y semillas cuando cambien las métricas. Usa días vacíos independientes y distingue la jornada del vaciado.
- Mantén los CSV y gráficos reproducibles en `results/` y `figures/`. Registra los prompts de desarrollo en `prompts/`.


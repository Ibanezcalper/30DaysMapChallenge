# Calendario de desafíos de mapas de 30 días

Este repositorio documenta el desarrollo y las soluciones a los retos del evento anual 30DayMapChallenge. Cada día del mes de noviembre plantea un tema cartográfico específico, el cual se resuelve utilizando herramientas de análisis espacial, programación en Python y conjuntos de datos geográficos reales.

El índice completo con los temas diarios, los retos técnicos propuestos, las fuentes de datos y los objetivos de análisis se encuentra detallado en el archivo indice.md en la raíz del proyecto.

## Problema que resuelve

El análisis y procesamiento de información geográfica suelen presentar barreras de entrada debido a la complejidad de las herramientas de software tradicionales de sistemas de información geográfica y a la falta de flujos de trabajo reproducibles mediante código. 

Este repositorio resuelve estas limitaciones al proporcionar:
- Flujos de trabajo reproducibles en Python para la limpieza, auditoría y análisis de datos geográficos.
- Ejemplos prácticos de integración de datos provenientes de organismos oficiales como el INEGI (DENUE, Red Vial Nacional, Marco Geoestadístico) y plataformas colaborativas como OpenStreetMap.
- Plantillas de visualización cartográfica estática de alta calidad utilizando bibliotecas de código abierto, lo que elimina la dependencia de software propietario de escritorio.

## Tecnologías utilizadas

El proyecto se desarrolla principalmente utilizando el lenguaje de programación Python y su ecosistema de análisis de datos geoespaciales. Las tecnologías y bibliotecas clave incluyen:
- Python: lenguaje de programación principal.
- Jupyter Notebooks: entorno interactivo utilizado para documentar, explicar y ejecutar el código de análisis paso a paso.
- GeoPandas: biblioteca para manipulación y análisis de datos vectoriales geográficos, extendiendo las capacidades de Pandas.
- Pandas: manipulación, limpieza y estructuración de tablas de datos estructurados.
- Matplotlib: motor de renderizado gráfico y diseño cartográfico para la generación de los mapas finales en formato de imagen.
- Contextily: descarga e integración de mapas base estéticos (como mapas base de CartoDB o Stamen) directamente en las visualizaciones de Matplotlib.
- NumPy: soporte para cálculos numéricos y operaciones con matrices.
- Seaborn: visualización de datos estadísticos complementarios.

## Estructura del repositorio

El repositorio organiza el contenido de forma modular e independiente para cada día del reto. La estructura general se describe a continuación:
- 01_Dia1_Puntos: contiene el código, los datos y los mapas del día 1 (puntos).
  - 00_datos: carpeta reservada para almacenar los conjuntos de datos de entrada en formatos como Shapefile o GeoJSON.
  - 01_codigo: contiene el cuaderno Jupyter (Puntos.ipynb), su exportación en PDF (Puntos.pdf) y los archivos de imagen resultantes con los mapas terminados.
- 02_Dia2_Lineas: contiene la infraestructura del reto de líneas del día 2, dividida de la misma manera en datos y código.
- 03_Dia_3_Poligonos: contiene el cuaderno de análisis y los datos para la delimitación espacial del reto de polígonos del día 3.
- 04_Dia4_BadMap: auditoría y reparación de coordenadas GPS corruptas (coordenadas invertidas, signos rotos, outliers); incluye dataset sintético, notebook y mapas antes/después.
- indice.md: tabla resumen con la planificación de los 30 días, detallando los retos específicos, temas y fuentes de información.

## Casos de uso específicos

Este repositorio cubre problemas prácticos y soluciones aplicadas a la geografía y al análisis de negocios:
- Auditoría y limpieza de bases de datos de puntos: filtrado y normalización de textos mediante expresiones regulares (Regex) para identificar establecimientos específicos en el DENUE del INEGI.
- Análisis de saturación de mercado: cálculo de densidad de puntos de interés comercial en zonas urbanas para identificar oportunidades de negocio o áreas de sobreoferta.
- Análisis de conectividad de redes viales: estudio del trazado de calles y ciclovías para evaluar la accesibilidad urbana y optimizar procesos de logística y distribución.
- Normalización estadística en mapas coropléticos: representación visual correcta de variables socioeconómicas a nivel de AGEBs (Áreas Geoestadísticas Básicas) urbanas evitando los sesgos que produce mapear valores absolutos.
- Calidad de datos GPS: detección y reparación de coordenadas invertidas, signos incorrectos, nulos y outliers geográficos antes de alimentar ruteo o dashboards.

## Cuándo utilizar este repositorio

Este repositorio es una herramienta de referencia útil en los siguientes escenarios:
- Aprendizaje autodidacta: cuando necesite aprender a utilizar la biblioteca GeoPandas y otras herramientas del ecosistema geoespacial de Python mediante ejemplos aplicados.
- Procesamiento de datos de INEGI: cuando requiera cargar, proyectar y procesar cartografía oficial de México en Python de manera eficiente.
- Automatización de mapas: cuando desee migrar procesos manuales de software de escritorio (como QGIS o ArcGIS) a scripts automatizados y reproducibles.
- Inspiración cartográfica: cuando busque ideas de diseño, paletas de colores y combinación de datos para participar en desafíos de mapeo.

## Instrucciones de uso e instalación

Para ejecutar los cuadernos de análisis y reproducir los mapas en su entorno local, siga los siguientes pasos.

### Requisitos previos

Es necesario contar con Python 3.8 o superior instalado en el sistema.

### Preparación del entorno

Clone este repositorio en su equipo local:
```bash
git clone https://github.com/Ibanezcalper/30DaysMapChallenge.git
cd 30DaysMapChallenge
```

Cree un entorno virtual de Python para mantener aisladas las dependencias:
```bash
python3 -m venv venv
source venv/bin/activate
```

Instale las bibliotecas necesarias utilizando el gestor de paquetes de Python:
```bash
pip install --upgrade pip
pip install pandas geopandas matplotlib contextily numpy seaborn notebook
```

### Ejecución de los análisis

Inicie el servidor de Jupyter Notebook desde la raíz del proyecto:
```bash
jupyter notebook
```

Navegue en la interfaz del navegador hasta la carpeta del día que desea explorar (por ejemplo, `01_Dia1_Puntos/01_codigo/Puntos.ipynb`) y ejecute las celdas secuencialmente para observar el proceso de carga de datos, procesamiento y generación de mapas.

## Licencia y contribuciones

Este repositorio es de carácter abierto con fines educativos y de divulgación. Si desea proponer mejoras en la lógica de procesamiento o añadir nuevos recursos de análisis, puede abrir un reporte de error (issue) o enviar una propuesta de cambio (pull request).

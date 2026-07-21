# Thirty day map challenge calendar

This repository documents the development and solutions to the challenges of the annual 30DayMapChallenge event. Each day of November presents a specific cartographic theme, which is resolved using spatial analysis tools, Python programming, and real-world geographic datasets.

The complete index containing the daily themes, proposed technical challenges, data sources, and analysis objectives is detailed in the file index.md (named as indice.md) at the root of the project.

## Problem it solves

Geospatial data analysis and cartographic design often present entry barriers due to the complexity of traditional desktop geographic information systems (GIS) software and the lack of reproducible code-based workflows.

This repository resolves these limitations by providing:
- Reproducible Python workflows for cleaning, auditing, and analyzing geographic data.
- Practical examples of integrating data from official government agencies, such as INEGI (DENUE, National Road Network, Geostatistical Framework), and collaborative platforms like OpenStreetMap.
- High-quality static cartographic visualization templates using open-source libraries, removing dependency on proprietary desktop GIS tools.

## Technologies used

The project is developed primarily using the Python programming language and its ecosystem of geospatial data analysis libraries. Key technologies and libraries include:
- Python: the main programming language.
- Jupyter Notebooks: an interactive environment used to document, explain, and execute the analysis code step-by-step.
- GeoPandas: a library for manipulating and analyzing geographic vector data, extending the capabilities of Pandas.
- Pandas: data manipulation, cleaning, and structuring of tabular data.
- Matplotlib: the core plotting engine and cartographic layout tool used to generate final maps as image files.
- Contextily: downloading and integrating aesthetic basemaps (such as CartoDB or Stamen basemaps) directly into Matplotlib visualizations.
- NumPy: support for numerical calculations and array operations.
- Seaborn: complementary statistical data visualization.

## Repository structure

The repository organizes its content in a modular and independent manner for each day of the challenge. The general structure is described below:
- 01_Dia1_Puntos: contains the code, data, and maps for day 1 (points).
  - 00_datos: folder reserved to store input datasets in formats such as Shapefiles or GeoJSON.
  - 01_codigo: contains the Jupyter Notebook (Puntos.ipynb), its PDF export (Puntos.pdf), and the resulting image files of the completed maps.
- 02_Dia2_Lineas: contains the infrastructure of the line challenge for day 2, split in the same way into data and code.
- 03_Dia_3_Poligonos: contains the analysis notebook and data for the spatial delineation of the polygon challenge on day 3.
- 04_Dia4_BadMap: GPS coordinate audit and repair (swapped lat/lon, broken signs, outliers); includes a synthetic dirty dataset, notebook, and before/after maps.
- 05_Dia5_AnalogMap: georeferencing a field sketch (Condesa, CDMX) with GCPs; turns a scanned image into an actionable GIS layer.
- 06_Dia6_Raster: Valley of Mexico DEM, slope calculation, and logistics suitability index via map algebra.
- indice.md: a summary table with the 30-day planning, detailing specific challenges, themes, and data sources.

## Specific use cases

This repository covers practical problems and solutions applied to geography and business analytics:
- Auditing and cleaning point databases: filtering and normalizing text data using regular expressions (Regex) to identify specific business categories in the INEGI DENUE dataset.
- Market saturation analysis: calculating the density of commercial points of interest in urban areas to identify business opportunities or oversupply zones.
- Connectivity analysis of road networks: studying the layout of streets and bike lanes to evaluate urban accessibility and optimize logistics and distribution processes.
- Statistical normalization in choropleth maps: representing socioeconomic variables at the urban AGEB (Basic Geostatistical Area) level correctly, preventing the visual biases produced when mapping absolute values instead of ratios.
- GPS data quality: detecting and repairing swapped coordinates, wrong signs, nulls, and geographic outliers before feeding routing systems or dashboards.
- Sketch georeferencing: converting field-visit croquis into GIS layers using Ground Control Points (GCPs).
- Raster map algebra: deriving slope from a DEM and combining layers into a site-suitability index.

## When to use this repository

This repository serves as a useful reference tool in the following scenarios:
- Self-directed learning: when you need to learn how to use the GeoPandas library and other tools in the Python geospatial ecosystem through applied examples.
- Processing INEGI data: when you need to load, project, and process official cartography of Mexico in Python efficiently.
- Map automation: when you want to migrate manual processes in desktop GIS software (such as QGIS or ArcGIS) to automated and reproducible scripts.
- Cartographic inspiration: when looking for design ideas, color palettes, and data combinations to participate in mapping challenges.

## Usage and installation instructions

To run the analysis notebooks and reproduce the maps on your local environment, follow the steps below.

### Prerequisites

It is necessary to have Python 3.8 or higher installed on your system.

### Environment setup

Clone this repository to your local machine:
```bash
git clone https://github.com/Ibanezcalper/30DaysMapChallenge.git
cd 30DaysMapChallenge
```

Create a Python virtual environment to keep dependencies isolated:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required libraries using the Python package installer:
```bash
pip install --upgrade pip
pip install pandas geopandas matplotlib contextily numpy seaborn notebook
```

### Running the analysis notebooks

Start the Jupyter Notebook server from the project root:
```bash
jupyter notebook
```

Navigate through the browser interface to the folder of the day you wish to explore (for example, `01_Dia1_Puntos/01_codigo/Puntos.ipynb`) and run the cells sequentially to observe the data loading, processing, and map generation flow.

## License and contributions

This repository is open-source for educational and outreach purposes. If you wish to propose improvements to the processing logic or add new analysis resources, feel free to open an issue or submit a pull request.

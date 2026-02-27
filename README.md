# 🗺️ CartoGen – Automatic Cartographic Generalization
**Overview**

GenCar is a modular Python framework for automated multi-scale topographic generalization with explicit topological constraints and quantitative spatial validation.

The system was designed to bridge traditional cartographic theory with reproducible geospatial data engineering workflows.

Target scale transition: 1:25,000 → 1:50,000

---

**Problem Statement**

Multi-scale topographic map production requires:

- Structured feature selection rules
- Morphological preservation
- Hydrographic-topographic consistency
- Controlled geometric simplification

Traditional manual generalization is:

- Labor-intensive
- Difficult to standardize
- Hard to reproduce
- Not scalable for national mapping systems

Additionally, conventional simplification algorithms often break:
- Contour–river intersections
- Topological continuity
- Morphological integrity

GenCar proposes an automated, topology-aware generalization methodology to address these limitations.

---

**Solution Architecture**

The workflow is structured into modular processing stages:

**1. Scale-Based Feature Selection**

- Original contour interval: 10m
- Target interval: 20m
- Elevation modulus filtering

✔ Reduces visual density

✔ Preserves structural morphology

**2. Hydrographic Influence Modeling**

- Buffer generation around drainage network
- Identification of contour–river interaction zones
- Spatial constraint definition

✔ Detects topological dependencies

✔ Defines simplification restriction zones

**3. Intersection Preservation Logic**

- Overlay between contours and hydrography
- Extraction of intersection vertices
- Fixed vertex tagging

✔ Prevents topological rupture

✔ Maintains hydrological continuity

**4. Modified Douglas–Peucker Algorithm**

- The standard Douglas–Peucker algorithm was adapted to:
- Preserve fixed (topological) vertices
- Apply controlled epsilon tolerance
- Maintain vertex sequence order
- Avoid fragmentation

✔ Reduces redundant vertices

✔ Preserves morphological integrity

✔ Supports recursive constrained simplification

**5. Quantitative Spatial Evaluation**

Generalization quality is assessed using:

- Vertex count reduction
- Total length comparison
- Hausdorff Distance (geometric similarity metric)

This enables:

- Objective validation
- Scenario comparison
- Parameter calibration

---

**Technical Highlights**

- Topology-aware geometric simplification
- Hydrographic-constrained generalization logic
- Modular spatial processing pipeline
- Quantitative validation framework
- Reproducible GeoDataFrame-based workflow

---

**Tech Stack**

- Python 3
- GeoPandas
- Shapely
- NumPy
- Matplotlib
- QGIS (visual validation)

Data Model:

- Shapefile (.shp)
- GeoDataFrame-based processing pipeline

---

**Repository Structure**

GenCar/
│

├── data/

├── scripts/

│   ├── douglas-peucker.py

│   ├── douglas+hausdorff.py

│

├── outputs/

└── README.md

Designed for modular scalability and research extensibility.

---

**Applications**

Systematic topographic mapping

National cartographic production workflows

Automated scale transitions

Topology-preserving map generalization

Spatial algorithm research

---

**Future Improvements**

Adaptive epsilon based on terrain curvature

Multi-scale automation (1:100k, 1:250k)

PostGIS integration

Performance optimization for large datasets

Extension to urban feature generalization

---

Authors

Luiza Werli Rosa
Thiago Wallace Nascimento da Paz
Geospatial Data Engineering & Cartographic Automation

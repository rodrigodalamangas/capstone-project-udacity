# Starbucks Offer Recommendation Engine

## Table of Contents

1. [Project Motivation](#motivation)
2. [Getting Started](#getting_started)
   - [Dependencies](#dependencies)
   - [Installing](#installation)
   - [Executing Program](#execution)
   - [Important Files](#importantfiles)
4. [Analysis Summary](#analysis)
4. [Author](#author)

<a name="motivation"></a>
## Project Motivation

This project was done as a requirement for the Udacity Data Scientist Nanodegree. The goal of the project is to use the transactional, customer and offer data to provide offer recommendations engine to Starbucks customers. The data was obtained by a simulation of the Starbucks mobile app in which customers receive and view offers, and pay their drinks in the stores.

<a name="getting_started"></a>
## Getting Started

<a name="dependencies"></a>
### Dependencies

- Python 3
- Data Libraries: NumPy, SciPy, Pandas
- SQLlite Database Libraries: SQLalchemy
- Web App and Data Visualization: Jupyter Notebook, Flask, Plotly

<a name="installation"></a>
### Installing

Clone the git repository:

```
git clone https://github.com/rodrigodalamangas/capstone-project-udacity.git
```

<a name="execution"></a>
### Executing Program:

1. Run the following commands in the project's root directory to set up your database.

   - To run ETL pipeline that cleans data and stores in database
     `python etl_pipeline.py`

2. Run the following command in the project's root directory to run your web app.
   `python run.py`

3. Go to http://0.0.0.0:3001/

<a name="importantfiles"></a>
### Important Files

**data/\***: CSV files and SQLite database

**templates/\***: templates/html files for web app

**etl_pipeline.py**: Extract Train Load (ETL) pipeline used for data cleaning, feature extraction, and storing data in a SQLite database

**recommendation_system.py**: Offer Recommendation Engine Model

**run.py**: This file can be used to launch the Flask web app used to recommend offers for Starbucks customers

**Starbucks Capstone Notebook**: The report of this project, shows all the analysis step by step

<a name="analysis"></a>
## Analysis Summary

In this stage, we analyzed the population based on their demographics and their spending behavior. We also took into account the interactions between the customers and the offers provided.

<a name="author"></a>
## Author

- [Rodrigo Dalamangas](https://github.com/rodrigodalamangas)
# Purpose of database 

- Use to store song play data
- Base on database to analyze the behavior of users
 

# How to run the scripts

1. Run `create_tables.py` first: `python create_tables.py`
2. Run `etl.py`: `python etl.py`
 

# Project structures
  
- `data`: folder contains log files
- `create_tables.py`: drop old tables and create new tables
- `elt.py`: process data and store them into database
- `README.md`: README file
- `sql_queries.py`: queries to drop, create tables, insert data, ...
- `test.ipynb` & `etl.ipynb`: to test functions from our files & `etl.ipynb` to build ETL pipeline

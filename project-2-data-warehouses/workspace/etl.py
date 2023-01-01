import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
        Load data from S3 to staging tables on Redshift
        
        Arguments:
        * cur: cursor to execute SQL query
        * con: connect to database
    """
    for query in copy_table_queries:
        print(f"=====Processing query {query}=====")
        cur.execute(query)
        conn.commit()
        print(f"=====Done processed query {query}=====")

    print("Successful load data into staging tables")


def insert_tables(cur, conn):
    """
        Insert data from staging tables to analytics tables on Redshift
        
        Arguments:
        * cur: cursor to execute SQL query
        * con: connect to database
    """
    for query in insert_table_queries:
        print(f"=====Processing query {query}=====")
        cur.execute(query)
        conn.commit()
        print(f"=====Done processed query {query}=====")

    print("Successful load data into analytics tables")


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()
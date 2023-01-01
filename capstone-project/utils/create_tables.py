import pandas as pd
from pyspark.sql import SparkSession
import seaborn as sns
import matplotlib.pyplot as plt
import os
import configparser
import datetime as dt

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
from pyspark.sql import SQLContext
from pyspark.sql.functions import isnan, when, count, col, udf, dayofmonth, dayofweek, month, year, weekofyear
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.types import *

import plotly.plotly as py
import plotly.graph_objs as go
import requests
requests.packages.urllib3.disable_warnings()

from pyspark.sql.functions import monotonically_increasing_id, year, month, dayofmonth, weekofyear, date_format

from pyspark.sql import SparkSession, SQLContext, GroupedData, HiveContext
from pyspark.sql.functions import *
from pyspark.sql.functions import date_add as d_add
from pyspark.sql.types import DoubleType, StringType, IntegerType, FloatType
from pyspark.sql import functions as F
from pyspark.sql.functions import lit
from pyspark.sql import Row

import datetime, time

from .tools import *


def create_dim_airport(input_df, output_data):
    """
        Gather airport data, create dataframe and write data into parquet files.
        
        :param input_df: dataframe of input data.
        :param output_data: path to write data to.
        :return: dataframe representing airport dimension
    """
    
    df = input_df.select(["ident", "type", "name", "elevation_ft", "iso_country", "iso_region", "municipality", "gps_code", "iata_code", "coordinates"])\
                .dropDuplicates(["ident"])
    
    write_to_parquet(df, output_data, "airport")
    
    return df


def create_dim_status(input_df, output_data):
    """
        Gather status data, create dataframe and write data into parquet files.
        
        :param input_df: dataframe of input data.
        :param output_data: path to write data to.
        :return: dataframe representing status dimension
    """
    
    df = input_df.withColumn("status_flag_id", monotonically_increasing_id()) \
                .select(["status_flag_id", "entdepa", "entdepd", "matflag"]) \
                .withColumnRenamed("entdepa", "arrival_flag")\
                .withColumnRenamed("entdepd", "departure_flag")\
                .withColumnRenamed("matflag", "match_flag")\
                .dropDuplicates(["arrival_flag", "departure_flag", "match_flag"])
    
    write_to_parquet(df, output_data, "status")
    
    return df


def create_dim_person(input_df, output_data):
    """
        Gather migrant data, create dataframe and write data into parquet files.
        
        :param input_df: dataframe of input data.
        :param output_data: path to write data to.
        :return: dataframe representing migrant dimension
    """
    
    df = input_df.withColumn("person_id", monotonically_increasing_id()) \
                .select(["person_id", "biryear", "gender"]) \
                .withColumnRenamed("biryear", "birth_year")\
                .dropDuplicates(["birth_year", "gender"])
    
    write_to_parquet(df, output_data, "person")
    
    return df


def create_dim_visa(input_df, output_data):
    """
        Gather visa data, create dataframe and write data into parquet files.
        
        :param input_df: dataframe of input data.
        :param output_data: path to write data to.
        :return: dataframe representing visa dimension
    """
    
    df = input_df.withColumn("visa_id", monotonically_increasing_id()) \
                .select(["visa_id","i94visa", "visatype", "visapost"]) \
                .dropDuplicates(["i94visa", "visatype", "visapost"])
    
    write_to_parquet(df, output_data, "visa")
    
    return df


def create_dim_country(input_df, output_data):
    """
        Gather country data, create dataframe and write data into parquet files.
        
        :param input_df: dataframe of input data.
        :param output_data: path to write data to.
        :return: dataframe representing country dimension
    """
    df = input_df
    
    write_to_parquet(df, output_data, "country")
    
    return df


def create_dim_state(input_df, output_data):
    """
        Gather state data, create dataframe and write data into parquet files.
        
        :param input_df: dataframe of input data.
        :param output_data: path to write data to.
        :return: dataframe representing state dimension
    """
    
    df = input_df.select(["State Code", "State", "Median Age", "Male Population", "Female Population", "Total Population", "Average Household Size",\
                          "Foreign-born", "Race", "Count"])\
                .withColumnRenamed("State Code", "state_code")\
                .withColumnRenamed("Median Age", "median_age")\
                .withColumnRenamed("Male Population", "male_population")\
                .withColumnRenamed("Female Population", "female_population")\
                .withColumnRenamed("Total Population", "total_population")\
                .withColumnRenamed("Average Household Size", "average_household_size")\
                .withColumnRenamed("Foreign-born", "foreign_born")
    
    df = df.groupBy(col("state_code"), col("State").alias("state")).agg(
                round(mean('median_age'), 2).alias("median_age"),\
                sum("total_population").alias("total_population"),\
                sum("male_population").alias("male_population"), \
                sum("female_population").alias("female_population"),\
                sum("foreign_born").alias("foreign_born"), \
                round(mean("average_household_size"),2).alias("average_household_size")
                ).dropna()
    
    write_to_parquet(df, output_data, "state")
    
    return df


def create_dim_time(input_df, output_data):
    """
        Gather time data, create dataframe and write data into parquet files.
        
        :param input_df: dataframe of input data.
        :param output_data: path to write data to.
        :return: dataframe representing time dimension
    """
    
    from datetime import datetime, timedelta
    from pyspark.sql import types as T
    
    def convert_datetime(x):
        try:
            start = datetime(1960, 1, 1)
            return start + timedelta(days=int(x))
        except:
            return None
    
    udf_datetime_from_sas = udf(lambda x: convert_datetime(x), T.DateType())

    df = input_df.select(["arrdate"])\
                .withColumn("arrival_date", udf_datetime_from_sas("arrdate")) \
                .withColumn('day', F.dayofmonth('arrival_date')) \
                .withColumn('month', F.month('arrival_date')) \
                .withColumn('year', F.year('arrival_date')) \
                .withColumn('week', F.weekofyear('arrival_date')) \
                .withColumn('weekday', F.dayofweek('arrival_date'))\
                .select(["arrdate", "arrival_date", "day", "month", "year", "week", "weekday"])\
                .dropDuplicates(["arrdate"])
    
    write_to_parquet(df, output_data, "time")
    
    return df


def create_fact_immigration(immigration_spark, output_data, spark):
    """
        Gather immigration data, create dataframe and write data into parquet files.
        
        :param input_df: dataframe of input data.
        :param output_data: path to write data to.
        :return: dataframe representing immigration fact
    """
    airport = spark.read.parquet("tables/airport")
    status = spark.read.parquet("tables/status")
    person = spark.read.parquet("tables/person")
    visa = spark.read.parquet("tables/visa")
    country = spark.read.parquet("tables/country")
    state = spark.read.parquet("tables/state")
    time = spark.read.parquet("tables/time")

    # join all tables to immigration
    df = immigration_spark.select(["*"])\
                .join(airport, (immigration_spark.i94port == airport.ident), how='full')\
                .join(person, (immigration_spark.biryear == person.birth_year) & (immigration_spark.gender == person.gender), how='full')\
                .join(status, (immigration_spark.entdepa == status.arrival_flag) & (immigration_spark.entdepd == status.departure_flag) &\
                      (immigration_spark.matflag == status.match_flag), how='full')\
                .join(visa, (immigration_spark.i94visa == visa.i94visa) & (immigration_spark.visatype == visa.visatype)\
                      & (immigration_spark.visapost == visa.visapost), how='full')\
                .join(state, (immigration_spark.i94addr == state.state_code), how='full')\
                .join(time, (immigration_spark.arrdate == time.arrdate), how='full')\
                .where(col('cicid').isNotNull())\
                .select(["cicid", "ident", "status_flag_id", "person_id", "visa_id", time.arrdate.alias("arrdate"), "state_code", \
                         "i94res", "depdate", "i94mode", "i94port", "i94cit", "i94addr", "airline", "fltno"])
    
    write_to_parquet(df, output_data, "immigration")
    
    return df
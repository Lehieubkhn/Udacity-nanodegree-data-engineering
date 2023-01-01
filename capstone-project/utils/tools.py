import pandas as pd
import numpy as np


def write_to_parquet(df, output_path, table_name):
    """
        Writes the dataframe as parquet file.
        
        :param df: dataframe to write
        :param output_path: output path where to write
        :param table_name: name of the table
    """
    
    file_path = output_path + table_name
    
    print("Writing table {} to {}".format(table_name, file_path))
    
    df.write.mode("overwrite").parquet(file_path)
    
    print("Write complete!")
    

def perform_quality_check(input_df, table_name):
    """Check data completeness by ensuring there are records in each table.
        :param input_df: spark dataframe to check counts on.
        :param table_name: name of table
    """
    
    record_count = input_df.count()

    if (record_count == 0):
        print("Data quality check failed for {} with zero records!".format(table_name))
    else:
        print("Data quality check passed for {} with record_count: {} records.".format(table_name, record_count))
        
    return 0
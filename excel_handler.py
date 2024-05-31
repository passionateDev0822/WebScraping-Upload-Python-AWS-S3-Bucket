# excel_handler.py

import pandas as pd
from config import EXCEL_FILE_PATH
import logging

def extract_item_numbers():
    try:
        with pd.ExcelFile(EXCEL_FILE_PATH) as xls:
            df = pd.read_excel(xls, sheet_name='Sheet1')
        return df['Style']
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
        return pd.Series()

def update_excel_with_urls(item_number, urls):
    print("Inserting urls of images and video")
    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name='Sheet1')
    row_index = df.index[df['Style'] == item_number][0]
    
    for i, url in enumerate(urls):
        if i == len(urls)-1:
            column_name = f"Video URL"
            df.at[row_index, column_name] = url
        else:
            column_name = f"Image URL {i+1}"
            if column_name not in df.columns:
                df[column_name] = None
            df.at[row_index, column_name] = url
    
    df.to_excel(EXCEL_FILE_PATH, index=False)

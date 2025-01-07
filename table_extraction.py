import json
from unstructured.partition.pdf import partition_pdf
import pandas as pd

def extract_tables_from_pdf(filename, strategy='hi_res'):
    """
    Extracts tables from a PDF file using the unstructured library.
    
    Args:
        filename (str): Path to the PDF file.
        strategy (str): Strategy for table extraction, default is 'hi_res'.
        
    Returns:
        tuple: List of pandas DataFrames and list of HTML representations of the tables.
    """
    elements = partition_pdf(
        filename=filename,
        infer_table_structure=True,
        strategy=strategy,
    )
    tables = [el for el in elements if el.category == "Table"]
    table_dicts = [el.to_dict() for el in tables]
    table_html = [el.metadata.text_as_html for el in tables]
    dfs = [pd.read_html(html)[0] for html in table_html]
    return dfs, table_html

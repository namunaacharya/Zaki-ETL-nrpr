import os
import ijson
import json
import gzip
import logging
import argparse
import zipfile
from decimal import Decimal

def con_decimal(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def file_type(file_path, nr_path, pr_path, nrpr_path, logger):
    if file_path.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as z:
            for data in z.namelist():
                with z.open(data, 'r') as f:
                    return process_file(f, nr_path, pr_path, nrpr_path, logger)
                
    elif file_path.endswith('.json.gz'):
        with gzip.open(file_path, 'rt') as f:
            return process_file(f, nr_path, pr_path, nrpr_path, logger)
        
    elif file_path.endswith('.json'):
        with open(file_path, 'rt') as f:
            return process_file(f, nr_path, pr_path, nrpr_path, logger)
        
    else:
        logger.info(f"Filetype unrecognizable {file_path}")
        return None

def process_file(f, nr_path, pr_path, nrpr_path, logger):
    provider_exists = False

    for item in ijson.items(f, 'provider_references.item'):
        provider_exists = True
        break
    
    f.seek(0)

    if provider_exists:
        logger.info("Extracting NR-PR file.")
        os.makedirs(nr_path, exist_ok=True)
        os.makedirs(pr_path, exist_ok=True)
        nr_file = os.path.join(nr_path, 'nr.json')
        pr_file = os.path.join(pr_path, 'pr.json')
        
        with open(nr_file, 'w') as in_file:
            for item in ijson.items(f, 'in_network.item'):
                in_file.write(json.dumps(item, default=con_decimal) + '\n')
        
        f.seek(0)  

        with open(pr_file, 'w') as prov_file:
            for item in ijson.items(f, 'provider_references.item'):
                prov_file.write(json.dumps(item, default=con_decimal) + '\n')
    else:
        logger.info("Extracting NRPR file.")
        os.makedirs(nrpr_path, exist_ok=True)      
        nrpr_file = os.path.join(nrpr_path, 'nrpr.json')

        with open(nrpr_file, 'w') as in_file:
            for item in ijson.items(f, ''):
                in_file.write(json.dumps(item,default=con_decimal) + '\n')
    
    return nr_path, pr_path, nrpr_path

def extract_import(input, logger):
    logger.info("Starting extract process")

    source = os.path.join(input, 'source')
    nr_path = os.path.join(input, 'nr')
    pr_path = os.path.join(input, 'pr')
    nrpr_path = os.path.join(input, 'nrpr')

    for file in os.listdir(source):
        file_path = os.path.join(source, file)
        try:
            file_type(file_path, nr_path, pr_path, nrpr_path, logger)
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    logger.info("File extraction completed successfully")
    return nr_path, pr_path, nrpr_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Process")
    parser.add_argument('input',help='Input folder path for ETL process')
    args = parser.parse_args()
    
    logging.basicConfig(filename="ETLnrpr.log",encoding='utf-8',level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger("Extract")

    nr_path, pr_path, nrpr_path = extract_import(args.input, logger)
import argparse
import logging
from etl import ETL

def main():
    logging.basicConfig(filename="ETLnrpr.log",encoding='utf-8',level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger("Logger")

    parser = argparse.ArgumentParser(description="ETL Process")
    parser.add_argument('input',help='Input folder path for ETL process')
    args = parser.parse_args()

    etl = ETL()
    etl.execute(args,logger)

if __name__ == "__main__":
    main()
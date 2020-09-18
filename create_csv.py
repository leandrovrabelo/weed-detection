#!/usr/bin/python3

from datetime import datetime
import csv

def create_csv(PATH_TO_CSV):

    # Creating a file with the column name, so the algorithm dont need to check if it's inserted correctly
    today = datetime.today().isoformat()[0:10]
    csv_file = PATH_TO_CSV+f'{today}-bbox-modulo-01.csv'
        
    with open(csv_file, 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['filename',
                        'width',
                        'height',
                        'class',
                        'xmin',
                        'ymin',
                        'xmax',
                        'ymax',
                        'position'])

    return csv_file
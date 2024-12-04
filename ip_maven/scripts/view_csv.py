import csv
import argparse

def display_rows_in_range(csv_file, start_row, stop_row):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i + 1 >= start_row:
                print(row)
            if i + 1 >= stop_row:
                break

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='create csv')
    parser.add_argument('--csv', required=True, help='Path to the CSV file to import.')
    args = parser.parse_args()

    start_row = 4000  # Specify the start row
    stop_row = 5010   # Specify the stop row
    display_rows_in_range(args.csv, start_row, stop_row)


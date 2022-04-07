import csv
import argparse
import json

parser = argparse.ArgumentParser(description='Convert Kraken OHLCV timeframe data into .json for Freqtrade.')
parser.add_argument('-i', '--input', help='Input file.')
parser.add_argument('-o', '--output', help='File to write to.')
args = parser.parse_args()

if args.input == None or args.output == None:
    parser.print_help()

formatted = []
with open(args.input, newline='') as csvfile:
    data = csv.reader(csvfile)
    for row in data:
        formatted.append(row)

with open(args.output, 'w+') as outfile:
    json.dump(formatted, outfile)
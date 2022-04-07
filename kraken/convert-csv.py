#!/usr/bin/env python

import zipfile
import os
import sys
import re
import pandas as pd
import argparse
from pathlib import Path


parser = argparse.ArgumentParser(description='Kraken OHLCVT converter. Created by planet-winter on github, modified by chanka0.')
parser.add_argument('-i', '--input', help='Input zip file.', required=True)
parser.add_argument('-o', '--output-dir', help='Output directory of converted files.')
parser.add_argument('-c', '--cleanup', help='Delete extracted unconverted files.', type=bool)
args = parser.parse_args()
if (args.input == None):
    parser.print_help()
    exit()

def export_json(df, exchange='kraken', currency=None, quote_currency=None, timeframe=None):
    filename = "%s_%s-%s.json" % (currency, quote_currency, timeframe)

    print("exporting ", filename)

    Path(exchange).mkdir(exist_ok=True)
    file_path = "%s%s%s" % (exchange, os.path.sep, filename)

    df.to_json(file_path, orient='values')

def ccxt_timeframe(minutes):
    timeframe_lookup = {"1": "1m",
                        "5": "5m",
                        "15": "15m",
                        "60": "1h",
                        "720": "12h",
                        "1440": "1d"
                        }
    return timeframe_lookup[minutes]

def main():
    origin_url = "https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data"
    unzip_dirname = "extracted"

    print("-" * 30)
    print("I convert a kraken ohlcvt zip to freqtrade json")
    print("expecting zip file named ", args.input, "in cwd")
    print("download the zip from this page: ", origin_url)
    print("-" * 30)

    if not Path(args.input).exists():
        print("File {} cannot be found.".format(args.input))
        sys.exit(1)

    Path(unzip_dirname).mkdir(exist_ok=True)
    with zipfile.ZipFile(args.input, 'r') as zip:
        print("Starting extraction of zipped files")
        zip.extractall(unzip_dirname)

    path_list = Path(unzip_dirname).glob('**/*.csv')
    for path in path_list:
        csv_path = str(path)
        csv_name = path.name

        components_re = re.compile('^(?P<currency>\w[^_]+)(?P<quote_currency>(USD)|(USDT)|(USDC)|(ZUSD)|(EUR)|(AUD)|(CAD)|(CHF)|(JPY)|(GBT)|(XBT)|(ETH)[^_]+)_(?P<minutes>\d+)\.csv$')
        components = re.search(components_re, csv_name)
        if components is not None:
            df = pd.read_csv(csv_path,
                             names=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades'],
                             usecols=['timestamp', 'open', 'high', 'low','close', 'volume']
                             )
            df.timestamp = df.timestamp * 1000
            export_json(df,
                        currency=components["currency"],
                        quote_currency=components["quote_currency"],
                        timeframe=ccxt_timeframe(components["minutes"])
                       )
    if (args.cleanup):
        os.rmdir(unzip_dirname)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: dev_monitoring_streams.py
#
# Part of ‘UNICORN Binance Local Depth Cache’
# Project website: https://github.com/LUCIT-Systems-and-Development/unicorn-binance-local-depth-cache
# Github: https://github.com/LUCIT-Systems-and-Development/unicorn-binance-local-depth-cache
# Documentation: https://unicorn-binance-local-depth-cache.docs.lucit.tech
# PyPI: https://pypi.org/project/unicorn-binance-local-depth-cache
#
# Author: LUCIT Systems and Development
#
# Copyright (c) 2022-2023, LUCIT Systems and Development (https://www.lucit.tech) and Oliver Zehentleitner
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from unicorn_binance_local_depth_cache import BinanceLocalDepthCacheManager, DepthCacheOutOfSync
import logging
import os
import sys
import time

try:
    from unicorn_binance_rest_api import BinanceRestApiManager
except ImportError:
    print("Please install `unicorn-binance-rest-api`! https://pypi.org/project/unicorn-binance-rest-api/")
    sys.exit(1)

logging.getLogger("unicorn_binance_local_depth_cache")
logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

spawn_depth_caches = 20
update_interval_milliseconds = 100
exchange = "binance.com"

ubra = BinanceRestApiManager("*", "*", exchange=exchange)
ubldc = BinanceLocalDepthCacheManager(exchange=exchange, ubra_manager=ubra)

markets = []
data = ubra.get_all_tickers()
for item in data:
    markets.append(item['symbol'])

print(f"Starting {spawn_depth_caches} new depth caches with update_interval={update_interval_milliseconds}")
ubldc.create_depth_cache(markets=markets[:spawn_depth_caches], update_interval=update_interval_milliseconds)

while True:
    try:
        top_asks = ubldc.get_asks(market=markets[0])[:3]
        top_bids = ubldc.get_bids(market=markets[0])[:3]
    except DepthCacheOutOfSync:
        top_asks = "Out of sync!"
        top_bids = "Out of sync!"
    text = f"top 3 asks: {top_asks}\r\n top 3 bids: {top_bids}"
    ubldc.print_summary(add_string=text)
    time.sleep(1)


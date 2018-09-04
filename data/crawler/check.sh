#!/bin/bash

echo "change num:" `cat $1/crawler.txt | wc -l`

echo "null text num:" `cat $1/crawler.txt | grep '"text": "-"' | wc -l`

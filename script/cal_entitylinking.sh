#!/bin/bash

# 用于统计两年行政区划变更情况

DATAPATH=`cd ./../data/tmp;pwd`

echo "$1 lines:"
wc -l $1
echo "$2 lines:"
wc -l $2


echo "$1 has and $2 has"
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && ($1 in city) && ($2==city[$1]) {print $1,$2,city[$1]}' $1 $2 | wc -l


echo "$1 has and $2 has, but name changed:"
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && ($1 in city) && !($2==city[$1]) {print $1,$2,city[$1]}' $1 $2 | wc -l
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && ($1 in city) && !($2==city[$1]) {print $1,$2,city[$1]}' $1 $2 > ${DATAPATH}/$1_$2_has_name_changed
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && ($1 in city) && !($2==city[$1]) {print $1,$2,city[$1]}' $1 $2


echo "$2 has but $1 no":
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && !($1 in city) {print $1,$2,city[$1]}' $1 $2 | wc -l
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && !($1 in city) {print $1,$2,city[$1]}' $1 $2 > ${DATAPATH}/$2_has_$1_no
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && !($1 in city) {print $1,$2,city[$1]}' $1 $2


echo "$1 has but $2 no":
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && !($1 in city) {print $1,$2,city[$1]}' $2 $1 | wc -l
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && !($1 in city) {print $1,$2,city[$1]}' $2 $1 > ${DATAPATH}/$1_has_$2_no
awk -F'\t' 'BEGIN{OFS="\t"}NR==FNR{city[$1]=$2} NR!=FNR && !($1 in city) {print $1,$2,city[$1]}' $2 $1

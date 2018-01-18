#!/bin/bash
# Author: ShotaKitazawa

ANALYZED_FILE=${1:-"err: invalid command: bash $0 analyzed_file"}
echo "create values for HOT on network"
rm -f $(dirname $0)/network/*
python $(dirname $0)/create_values_network.py $ANALYZED_FILE
echo "create HOT on instances"
rm -f $(dirname $0)/hot-instances.yaml
python $(dirname $0)/create_hot_instances.py $ANALYZED_FILE

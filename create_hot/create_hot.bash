#!/bin/bash
# Author: ShotaKitazawa

ANALYZED_FILE=${1:-"err: invalid command: bash $0 analyzed_file"}
echo "create values for HOT on network"
python create_values_network.py $ANALYZED_FILE
echo "create HOT on instances"
python create_hot_instances.py $ANALYZED_FILE

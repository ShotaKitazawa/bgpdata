#!/bin/bash

TARGET_DIR=$(dirname $0)/instances
MATCH="  script_asn[0-9]*_1:"
FLAG=0

if [ ! -d $TARGET_DIR ]; then mkdir -p $TARGET_DIR; fi
rm -f $TARGET_DIR/*

cp $(dirname $0)/netconf.sh $TARGET_DIR
cp $(dirname $0)/gobgp.sh $TARGET_DIR

cnt=0
IFS=$'\n'; for line in $(cat $(dirname $0)/hot-instances.yaml); do
  if [[ $line == $MATCH ]]; then
    FILENAME=$TARGET_DIR/$cnt.yml
    let cnt++
    FLAG=1
  fi
  if [ $FLAG -eq 1 ]; then
    echo "heat_template_version: pike" >> $FILENAME
    echo "resources:" >> $FILENAME
    FLAG=0
  fi
  if [ "$line" = "        - { get_resource: security_group_allallow }" ]; then
    line="        - AllAllow"
  fi
  echo $line >> $FILENAME
done


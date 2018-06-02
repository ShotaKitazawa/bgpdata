#!/bin/bash
# Author: ShotaKitazawa

SUB_COMMAND=${1:-"create/delete"}
SCRIPT_DIR=$(cd $(dirname $0) && pwd)

if [ "$SUB_COMMAND" = "create" ]; then
  cd $SCRIPT_DIR/network
  for i in *; do
    openstack stack create -t $SCRIPT_DIR/hot-network.yaml --parameter "network-name=$i" --parameter-file "cidr=$SCRIPT_DIR/network/$i" as-$i
  done
  openstack stack create -t $(dirname $0)/hot-instances.yaml instances
elif [ "$SUB_COMMAND" = "delete" ]; then
  cd $SCRIPT_DIR/network
  for i in *; do
    openstack stack delete as-$i -y
  done
  openstack stack delete instances
fi

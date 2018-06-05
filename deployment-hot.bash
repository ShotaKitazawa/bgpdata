#!/bin/bash
# Author: ShotaKitazawa

SUB_COMMAND=${1:-"create/delete"}
HOT_DIR=$(cd $(dirname $0) && pwd)/create_hot/

if [ "$SUB_COMMAND" = "create" ]; then
  openstack stack create -t $HOT_DIR/hot-networks.yaml networks
  openstack stack create -t $HOT_DIR/hot-instances.yaml instances
elif [ "$SUB_COMMAND" = "delete" ]; then
  openstack stack delete instances -y
  echo "delete instances"
  openstack stack delete networks -y
  echo "delete networks"
else
  echo "invalid argument"
fi

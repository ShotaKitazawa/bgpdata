#!/bin/bash
# Author: ShotaKitazawa

SUB_COMMAND=${1:-"create/delete"}
SCRIPT_DIR=$(cd $(dirname $0) && pwd)

if [ "$SUB_COMMAND" = "create" ]; then
  openstack stack create -t $SCRIPT_DIR/hot-networks.yaml networks
  openstack stack create -t $SCRIPT_DIR/hot-instances.yaml instances
elif [ "$SUB_COMMAND" = "delete" ]; then
  openstack stack delete instances -y
  echo "delete instances"
  openstack stack delete networks -y
  echo "delete networks"
fi

#!/bin/bash
# Author: ShotaKitazawa

SUB_COMMAND=${1:-"create/delete"}

if [ "$SUB_COMMAND" = "create" ]; then
  for i in $(ls $(dirname $0)/network); do
    openstack stack create -t $(dirname $0)/hot-network.yaml --parameter "network-name=$i" --parameter-file "cidr=$i" $i
  done
  openstack stack create -t $(dirname $0)/hot-instances.yaml instances
elif [ "$SUB_COMMAND" = "delete" ]; then
  for i in $(ls $(dirname $0)/network); do
    openstack stack delete $i
  done
  openstack stack delete instances
fi

#!/bin/bash

MY_AS='$$my_as'
NEIGHBOR_ASES='$$neighbor_ases'
NEIGHBOR_ADDRS='$$neighbor_addresses'

cat << _EOF_ > /etc/gobgp/gobgpd.conf
[global]
  [global.config]
    as = $MY_AS
    router-id = "$MY_AS"
  [global.apply-policy.config]
    export-policy-list = ["policy1"]

[zebra]
  [zebra.config]
    enabled = true
    url = "unix:/var/run/quagga/zserv.api"


$(for i in $(seq 1 $(echo $NEIGHBOR_ASES | wc -w)); do
  NEIGHBOR_AS=$(echo $NEIGHBOR_ASES | cut -d " " -f $i)
  NEIGHBOR_ADDR=$(echo $NEIGHBOR_ADDRS | cut -d " " -f $i)
  echo
  echo "[[neighbors]]"
  echo "  [neighbors.config]"
  echo "    neighbor-address = '$NEIGHBOR_ADDR'"
  echo "    peer-as = $NEIGHBOR_AS"
  echo "  [[neighbors.afi-safis]]"
  echo "    [neighbors.afi-safis.config]"
  echo "       afi-safi-name = 'ipv4-unicast'"
done)

[[policy-definitions]]
  name = "policy1"
  [[policy-definitions.statements]]
    name = "statement1"
    [policy-definitions.statements.actions.bgp-actions]
      set-next-hop = "self"
    [policy-definitions.statements.actions]
      route-disposition = "accept-route"
_EOF_

systemctl enable gobgpd
systemctl restart gobgpd

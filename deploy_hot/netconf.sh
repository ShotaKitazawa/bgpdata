#!/bin/bash

IFACES='$$interfaces'
ADDRS='$$addresses'
NETWORKS='$$networks'
ADVERTISE_ADDRS='$$asaddresses'

# backup /etc/network/interfaces
yes no | mv -i /etc/network/interfaces{,.default}

# generate /etc/network/interfaces
echo "auto lo" >> /etc/network/interfaces
echo "iface lo inet loopback" >> /etc/network/interfaces
echo >> /etc/network/interfaces
for i in $(seq 1 $(echo $ADVERTISE_ADDRS | wc -w)); do
  NUM=$((i-1))
  ADVERTISE_ADDR=$(echo $ADVERTISE_ADDRS | cut -d " " -f $i)
  echo "auto lo:$NUM" >> /etc/network/interfaces
  echo "iface lo:$NUM inet static" >> /etc/network/interfaces
  echo "address $ADVERTISE_ADDR" >> /etc/network/interfaces
  echo >> /etc/network/interfaces
done
for i in $(seq 1 $(echo $IFACES | wc -w)); do
  IFACE=$(echo $IFACES | cut -d " " -f $i)
  ADDR=$(echo $ADDRS | cut -d " " -f $i)
  NETPREF=$(echo $NETWORKS | cut -d " " -f $i | cut -d '/' -f 2)
  echo "auto $IFACE" >> /etc/network/interfaces
  if [ "$ADDR" = "dhcp" ]; then
    echo "iface $IFACE inet dhcp" >> /etc/network/interfaces
  else
    echo "iface $IFACE inet static" >> /etc/network/interfaces
    echo "address $ADDR" >> /etc/network/interfaces
    echo "netmask $NETPREF" >> /etc/network/interfaces
  fi
  echo >> /etc/network/interfaces
done

# restart network.service
systemctl restart networking

# generate advertise.sh
if [ ! -d /root/bin ]; then mkdir /root/bin -p; fi
echo "#!/bin/bash" >> /root/bin/advertise.sh
echo "" >> /root/bin/advertise.sh
for i in $ADVERTISE_ADDRS; do
  echo "gobgp global rib add $i" >> /root/bin/advertise.sh
done

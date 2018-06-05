#!/bin/bash
# Author: ShotaKitazawa

EACH_RIB=false

RIB="rib.20180101.0000"
RIB="rib.20180101.0000"
PREFIX="
http://archive.routeviews.org/route-views.eqix/
http://archive.routeviews.org/route-views.isc/
http://archive.routeviews.org/route-views.kixp/
http://archive.routeviews.org/route-views.jinx/
http://archive.routeviews.org/route-views.linx/
http://archive.routeviews.org/route-views.nwax/
http://archive.routeviews.org/route-views.sydney/
http://archive.routeviews.org/route-views.saopaulo/
http://archive.routeviews.org/route-views.sg/
http://archive.routeviews.org/route-views.perth/
http://archive.routeviews.org/route-views.sfmix/
http://archive.routeviews.org/route-views.soxrs/
"
POSTFIX="bgpdata/2018.01/RIBS/$RIB.bz2"

for i in $PREFIX; do
  EXTENSION=$(echo ${i#*/} |perl -pe "s/^.*\.(.*)\/$/\1/g")
  if [ ! -f $RIB.$EXTENSION.raw ];then
    wget $i$POSTFIX
    bzip2 -d $RIB.bz2
    mv $RIB{,.$EXTENSION}
    echo "bgpdump $RIB.$EXTENSION > $RIB.$EXTENSION.raw"
    bgpdump $RIB.$EXTENSION > $RIB.$EXTENSION.raw
  fi
  if ($EACH_RIB); then
    echo "python analysis-rib.py $RIB.$EXTENSION.raw > result.$EXTENSION"
    python analysis-rib.py $RIB.$EXTENSION.raw > result.$EXTENSION
  fi
done

python analyze-rib.py $RIB.*.raw > result.all

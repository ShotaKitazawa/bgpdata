#!/bin/bash

TARGET=neighbors_100.txt
cat $(dirname $0)/$TARGET | egrep ^AS | wc -l


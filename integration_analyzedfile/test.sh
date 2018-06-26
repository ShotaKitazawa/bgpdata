#!/bin/bash

TARGET=addCombined.txt
cat $(dirname $0)/$TARGET | egrep ^AS | wc -l


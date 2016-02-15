#!/bin/csh -f

cd `dirname $0` && source impclacz.config

./pixload.csh ${IMAGE_DOWNLOADDIR} ${PIX_MAPPING}

#!/bin/sh
docker build -t navyplot .
docker run --rm -dit -v $(pwd)/data:/usr/src/app/data:z --name navy navyplot


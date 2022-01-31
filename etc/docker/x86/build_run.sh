#!/bin/bash

echo "Rebuilding container..."
docker build -f etc/docker/i386/Dockerfile -t multa_metrics_agent:0.1.0 .

echo "Running container..."
docker run --net=host --restart always --privileged -d --name multa_metrics_agent multa_metrics_agent:0.1.0
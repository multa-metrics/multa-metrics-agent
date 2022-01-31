#!/bin/bash

echo "Stopping container..."
docker container stop multa_metrics_agent && docker container rm multa_metrics_agent

echo "Rebuilding container..."
docker build -f etc/docker/x86/Dockerfile -t multa_metrics_agent:0.1.0 .

echo "Running container..."
docker run --net=host --restart always --privileged -d --name multa_metrics_agent multa_metrics_agent:0.1.0
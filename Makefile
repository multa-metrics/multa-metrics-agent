.PHONY: login build tag deploy
.DEFAULT_GOAL := help

SHELL := /bin/bash
LOGIN :=
REPO := 112646120612.dkr.ecr.us-east-1.amazonaws.com

IMAGE_I386 := python:3.7.7-slim-buster
IMAGE_ARMV7 := balenalib/generic-armv7ahf-ubuntu-python:3.7.7-eoan-run

PROJECT_I386 := multa-agent-i386
PROJECT_ARMV7 := multa-agent-armv7

VERSION=0.0.3

login:
	$(shell aws ecr get-login --no-include-email --region us-east-1)

build-i386:
	docker build -t ${PROJECT_I386} --build-arg BASE_IMAGE=${IMAGE_I386} --build-arg VERSION=${VERSION} -f etc/docker/i386/Dockerfile .

tag-i386:
	docker tag ${PROJECT_I386}:latest ${REPO}/${PROJECT_I386}:${VERSION}

push-i386:
	docker push ${REPO}/${PROJECT_I386}:${VERSION}

build-armv7:
	docker build -t ${PROJECT_ARMV7} --build-arg BASE_IMAGE=${IMAGE_ARMV7} --build-arg VERSION=${VERSION} -f etc/docker/armv7/Dockerfile .

tag-armv7:
	docker tag ${PROJECT_ARMV7}:latest ${REPO}/${PROJECT_ARMV7}:${VERSION}

push-armv7:
	docker push ${REPO}/${PROJECT_ARMV7}:${VERSION}
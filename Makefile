.PHONY: login build tag deploy
.DEFAULT_GOAL := help

SHELL := /bin/bash
LOGIN :=
REPO := 112646120612.dkr.ecr.us-east-1.amazonaws.com

PROJECT_X86 := multa-agent-x86

VERSION=0.1.0

login:
	$(shell aws ecr get-login --no-include-email --region us-east-1)

build-i386:
	docker build -t ${PROJECT_X86} --build-arg BASE_IMAGE=${IMAGE_I386} --build-arg VERSION=${VERSION} -f etc/docker/x86/Dockerfile .

tag-i386:
	docker tag ${PROJECT_X86}:latest ${REPO}/${PROJECT_X86}:${VERSION}

push-i386:
	docker push ${REPO}/${PROJECT_X86}:${VERSION}
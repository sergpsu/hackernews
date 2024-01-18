SHELL:=/bin/bash
run:
	python3 app/main.py

test:
	pytest

build:
	bash scripts/docker-build.sh

deploy:
	microk8s.kubectl create namespace hackernews --dry-run=client -o yaml | microk8s.kubectl apply -f -
	source .env.sh && envsubst < ./deployment/hackernews.yaml | microk8s.kubectl --namespace hackernews apply -f -

redeploy:
	microk8s.kubectl delete namespace hackernews || true
	microk8s.kubectl create namespace hackernews --dry-run=client -o yaml | microk8s.kubectl apply -f -
	source .env.sh && envsubst < ./deployment/hackernews.yaml | microk8s.kubectl --namespace hackernews apply -f -
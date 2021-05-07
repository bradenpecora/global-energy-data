  
NSPACE="bradenpecora"
APP="global-energy-data"
VER="1.0.0"
RPORT="6406"
FPORT="5026"
UID="869731"
GID="816966"

list-targets:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'


build-network:
	docker network create ${NSPACE}-network-test

build-db:
	docker build -t ${NSPACE}/${APP}-db:${VER} \
                     -f docker/Dockerfile.db \
                     ./

build-app:
	docker build -t ${NSPACE}/${APP}-app:${VER} \
                     -f docker/Dockerfile.app \
                     ./

test-db:
	docker run --name ${NSPACE}-db \
                   --network ${NSPACE}-network-test \
                   -p ${RPORT}:6379 \
                   -d \
                   -u ${UID}:${GID} \
                   -v ${PWD}/data/:/data \
                   ${NSPACE}/${APP}-db:${VER}

test-api:
	docker run --name ${NSPACE}-api \
                   --network ${NSPACE}-network-test \
                   --env REDIS_IP=${NSPACE}-db \
                   -p ${FPORT}:5000 \
                   -d \
                   ${NSPACE}/${APP}-app:${VER} api.py


test-wrk:
	docker run --name ${NSPACE}-wrk \
                   --network ${NSPACE}-network-test \
                   --env REDIS_IP=${NSPACE}-db \
                   -d \
                   ${NSPACE}/${APP}-app:${VER} worker.py

clean-db:
	docker ps -a | grep ${NSPACE}-db | awk '{print $$1}' | xargs docker rm -f

clean-api:
	docker ps -a | grep ${NSPACE}-api | awk '{print $$1}' | xargs docker rm -f

clean-wrk:
	docker ps -a | grep ${NSPACE}-wrk | awk '{print $$1}' | xargs docker rm -f



build-all: build-db build-app

test-all: test-db test-api test-wrk

clean-all: clean-db clean-api clean-wrk


k-test-db:
	kubectl apply -f k8s/test/db/bradenp-ged-test-redis-service.yml
	kubectl apply -f k8s/test/db

k-test-api:
	kubectl apply -f k8s/test/api

k-test-wrk:
	kubectl apply -f k8s/test/worker

k-test-all: k-test-db k-test-api k-test-wrk

k-prod-db:
	kubectl apply -f k8s/prod/db/bradenp-ged-prod-redis-service.yml
	kubectl apply -f k8s/prod/db

k-prod-api:
	kubectl apply -f k8s/prod/api

k-prod-wrk:
	kubectl apply -f k8s/prod/worker

k-prod-all: k-prod-db k-prod-api k-prod-wrk

push:
	git push
	git tag -a ${VER} -m "v ${VER}"
	git push origin ${VER}
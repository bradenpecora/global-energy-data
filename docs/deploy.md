# Deployment Instructions

There are currently two options for deploying the system. The user can chose to deploy the system in either Docker or Kubernetes. Instructions for both are included

## Docker

Navigate to `Makefile` and open it in a text editor. Environment variables are included in the first few lines of the file. Change accordingly. The NSPACE, APP and VER will be used in the name of docker images/containers. UID can be found with `id -u` and GID with `id -g` on the command line. 

A [docker network](https://docs.docker.com/network/network-tutorial-standalone/) is required. Create with the following:
```bash
[global-energy-data]$ make build-network
```

The list of networks can be found with `docker network ls`.

Build the database image and application image (for both the api and worker):

```bash
[global-energy-data]$ make build-db && make build-app
```

Run the containers:

```bash
[global-energy-data]$ make test-all
```

The containers are now up and running. Check with `docker ps -a`. See `user.md` for how to interact with the routes. To stop the containers:

```bash
[global-energy-data]$ make clean-all
```

For running or cleaning a specific container, change `all` to either `db`, `api`, or `wrk`.

## Kubernetes

Kubernetes pods run from docker images on DockerHub. I already have an [image](https://hub.docker.com/repository/docker/bradenpecora/global-energy-data-app/general) that is used and connected to this repository. The `test` environment uses the latest image, while the `prod` environment uses a specific tag of an image(see Line 25 of any of the flask/worker deployment files to configure). Alternatively, the user can push an image to DockerHub or have DockerHub build an image, and then configure the k8s cluster to pull that image for the worker and api pods.

There are files for deploying a test environment and production environment of this app. The following instructions will be for the `test` env. To use the `prod` environment, simply replace `test` with `prod` in the following instructions. 

We will need the redis service's IP before running the rest of the system, so this will be the first deployment/service started.

```bash
[global-energy-data]$ make k-test-db
```

Find the `CLUSTER-IP` of the service

```bash
[global-energy-data]$ kubectl get services
NAME                             TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
bradenp-ged-test-redis-service   ClusterIP   10.107.251.44    <none>        6379/TCP         148m
```

In my case, that would be `10.107.251.44`. Change the value of `REDIS_IP` in the flask and worker deployment files (line 33 and 29, respectively). Save the files and return to the home directory.

Apply everything else:

```bash
[global-energy-data]$ make k-test-all
```

Check if all of the following are running:

```bash
[global-energy-data]$ kubectl get all
NAME                                                      READY   STATUS    RESTARTS   AGE
pod/bradenp-ged-test-flask-deployment-fb78d868b-6gv9z     1/1     Running   6          115m
pod/bradenp-ged-test-redis-deployment-58fff7b48d-h65bh    1/1     Running   0          146m
pod/bradenp-ged-test-worker-deployment-85dfdc6f45-gqvmd   1/1     Running   0          107m
pod/bradenp-ged-test-worker-deployment-85dfdc6f45-sh284   1/1     Running   0          107m

NAME                                     TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
service/bradenp-ged-test-flask-service   ClusterIP   10.98.23.226     <none>        5000/TCP         145m
service/bradenp-ged-test-redis-service   ClusterIP   10.107.251.44    <none>        6379/TCP         158m

NAME                                                 READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/bradenp-ged-test-flask-deployment    1/1     1            1           145m
deployment.apps/bradenp-ged-test-redis-deployment    1/1     1            1           146m
deployment.apps/bradenp-ged-test-worker-deployment   2/2     2            2           107m

NAME                                                            DESIRED   CURRENT   READY   AGE
replicaset.apps/bradenp-ged-test-flask-deployment-5bcf59cbf9    0         0         0       125m
replicaset.apps/bradenp-ged-test-flask-deployment-f7b6bdbdf     0         0         0       145m
replicaset.apps/bradenp-ged-test-flask-deployment-fb78d868b     1         1         1       115m
replicaset.apps/bradenp-ged-test-redis-deployment-58fff7b48d    1         1         1       146m
replicaset.apps/bradenp-ged-test-worker-deployment-85dfdc6f45   2         2         2       107m
```

Everything should be deployed now. A resource can be deleted with the following:

```bash
kubectl delete <resource> <name>
```
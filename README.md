# Global Energy Data

This repository contains my final project submission for COE332. See prompt [here](https://coe-332-sp21.readthedocs.io/en/main/homework/final_project.html).
It contains a system of applications that can store, modify, and graph energy data from the [EIA](https://www.eia.gov/international/data/world).
This data is included.

## Applications
The following applications make up the system. They can be run in either a Docker container or a Kubernetes pod.

- global-energy-data-db: a Redis server that stores data
- global-energy-data-api: a Flask server that can be used for CRUD functionality and putting 'jobs' in the queue
- global-energy-data-wrk: a scalable worker that reads jobs from a queue and creates graphs of the data presented

## File Description

The following is a brief description of each file

```
- /data
    - dump.rdb   : dump for redis database
    - redis.conf : configuration for creating a redis image
    - olddata.json : data downloaded directly from EIA
    - newdata.json : formatted version of olddata.json
    - read_data.py : script for formatting olddata.json and creating newdata.json
- /docker
    - Dockerfile.app : Dockerfile for creating api and worker images
    - Dockerfile.db  : Dockerfile for creating redis db
- /docs
    - user.md : a readme for interacting with the system
    - deploy.md : a readme for deploying the system
    - /img
        - contains images for docs
- /k8s
    contains .yml files for creating a k8s system in either a production or testing environment
- /src
    - api.py  : contains script for running flask routes
    - data.py : contains functions used for finding keys given sub-parameters
    - jobs.py : contains script for queueing jobs and connecting to redis database
    - worker.py : contains script to generate image from job id
- Makefile : used for make commands (ease of access)
```
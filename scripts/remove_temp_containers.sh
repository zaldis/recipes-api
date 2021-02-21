#!/bin/bash

sudo docker ps -a | grep 'recipes-api_app_run' | cut -d' ' -f1 | xargs sudo docker rm

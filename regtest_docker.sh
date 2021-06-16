#!/bin/bash

docker-compose -f docker-compose.test.yml up --build -d db flask

docker-compose -f docker-compose.test.yml up test

docker-compose -f docker-compose.test.yml down

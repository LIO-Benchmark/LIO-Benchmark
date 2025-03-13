#!/bin/bash
docker build -t liobench:ubuntu20.04_cuda12.4.1_noetic --network=host -f Dockerfile .

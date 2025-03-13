#!/bin/bash
docker build -t liobench:ubuntu20.04_cuda11.1.1_noetic --network=host -f Dockerfile .

#!/bin/bash

python3 generate_dockerfile.py --ubuntu_version 20.04 --ros_version noetic --cuda_version 12.4.1
python3 generate_dockerfile.py --ubuntu_version 20.04 --ros_version noetic --cuda_version 11.1.1

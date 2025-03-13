# Docker installation

Docker can ensure that all developers in a project have a common, consistent development environment. It is recommended for beginners, casual users, people who are unfamiliar with Ubuntu.

## Step 1: Installing dependencies manually

- Install Nvidia driver
- Install Docker Engine
- Install Docker compose
- Install NVIDIA Container Toolkit

## Step 2: Import project

```bash
(host) $ git clone https://github.com/LIO-Benchmark/LIO-Benchmark ~/liobench/
```

## Step 3 (Option 1): Pulling the image from Docker Hub

See more in https://hub.docker.com/repository/docker/877381/rangenet/general

| Version                                       | Status                                                       |
| --------------------------------------------- | ------------------------------------------------------------ |
| 877381/liobench:ubuntu20.04_cuda11.1.1_noetic | [![Build image ubuntu20.04_cuda11.1.1_noetic](https://github.com/LIO-Benchmark/LIO-Benchmark/actions/workflows/build_image_ubuntu20.04_cuda11.1.1_noetic.yml/badge.svg)](https://github.com/LIO-Benchmark/LIO-Benchmark/actions/workflows/build_image_ubuntu20.04_cuda11.1.1_noetic.yml) |
| 877381/liobench:ubuntu20.04_cuda12.4.1_noetic | [![Build image ubuntu20.04_cuda12.4.1_noetic](https://github.com/LIO-Benchmark/LIO-Benchmark/actions/workflows/build_image_ubuntu20.04_cuda12.4.1_noetic.yml/badge.svg)](https://github.com/LIO-Benchmark/LIO-Benchmark/actions/workflows/build_image_ubuntu20.04_cuda12.4.1_noetic.yml) |

The image size is about 15.7 GB (after uncompressed), so make sure you have enough space

```bash
# e.g. docker pull 877381/lioben:ubuntu20.04_cuda11.1.1_noetic
(host) $ docker pull <image_name>

# Rename the image (remove the Docker user prefix)
(host) $ TAG=ubuntu20.04_cuda12.4.1_noetic && docker tag 877381/rangenet:${TAG} rangenet:${TAG}
```

> [!Note]
>
> The default image built here uses `user_id` 1000. To use a different `user_id`, modify the provided Dockerfile and build the image accordingly.

## Step 3 (Option 2): Create image by Dockerfile

- Open `generate_dockefile.sh` and modify the content to suit your needs. For available CUDA and cuDNN with specific versions, see more in https://hub.docker.com/r/nvidia/cuda/tags.

- Run `generate_dockerfile.sh` to generate the Dockerfile

```bash
(host) $ bash generate_dockerfile.sh
```

- cd to the directory containing the Dockerfile and run the following command to build the image

```bash
# Here is an example of building the image
(host) $ cd ubuntu20.04_cuda11.1.1_noetic
(host) $ bash build_image.sh
```

## Step 3: Run the container

After the image is built, you can run the container with the following command

```bash
# Please replace the image name with the name of the image you built or pulled
(host) $ cd ~/liobench/docker/ubuntu20.04_cuda11.1.1_noetic

# Please change the mount path in docker-compose.yml
(host) $ docker compose up
# Open an another terminal
(host) $ docker exec -it rangenet /bin/bash
```

## Step 4: Quick start

```bash
# In container
(host) $ cd ~/rangenet/src/rangenet/
(host) $ mkdir build
(host) $ unset ROS_VERSION && cd build && cmake .. && make -j4
(host) $ ./demo 
```

## Step 5: (Optional) 

- Enable hstr

```bash
(container) $ hstr --show-configuration >> ~/.bashrc && . ~/.bashrc
```

- Support ssh connection

```bash
(container) $ mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys

# Put the secreat key here
(container) $ vim ~/.ssh/authorized_keys

(container) $ vim ~/.bashrc
# eval "$(ssh-agent -s)" > /dev/null
# ssh-add ~/.ssh/<secret_file> 2>/dev/null
```

- Add hostname resolver

```bash
(container) $ sudo vim /et/hosts
# 140.82.116.3                 github.com
```

## Reference

- https://github.com/pytorch/TensorRT/blob/main/docker/Dockerfile
- https://github.com/Natsu-Akatsuki/RangeNet-TensorRT/blob/422bfb0f97f91e7363de8b9fff3131fdc1558547/docker/Dockerfile-tensorrt8.2.2


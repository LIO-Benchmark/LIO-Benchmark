from pathlib import Path
import argparse
import os
import re


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Dockerfile and related files.")
    parser.add_argument("--ubuntu_version", default="22.04", choices=["22.04", "20.04"], help="Ubuntu version (default: 22.04)")
    parser.add_argument("--ros_version", default="humble", choices=["noetic", "humble"], help="ROS version (default: humble)")
    parser.add_argument("--cuda_version", default="12.4.1", help="CUDA version (default: 12.4.1)")

    return parser.parse_args()


def generate_dockerfile(ubuntu_version, ros_version, cuda_version, target_dir):
    target_dir.mkdir(parents=True, exist_ok=True)

    def set_basic_image():
        if cuda_version == "11.1.1":
            return f"nvidia/cuda:{cuda_version}-cudnn8-devel-ubuntu{ubuntu_version}"
        else:
            return f"nvidia/cuda:{cuda_version}-cudnn-devel-ubuntu{ubuntu_version}"

    def set_ros():
        # Note: the default bash is /bin/sh, thus we do not use "source"
        tmp_dict = {
            "noetic": """
RUN DEBIAN_FRONTEND=noninteractive sh -c '. /etc/lsb-release && echo "deb http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/ `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list' \\
    && apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654 \\
    && apt update \\
    && DEBIAN_FRONTEND=noninteractive apt install -y ros-noetic-desktop-full \\
        python3-catkin-tools \\
        python3-rosdep \\
        python3-rosinstall \\
        python3-rosinstall-generator \\
        python3-wstool \\
        python3-pip \\
    && rm -rf /var/lib/apt/lists/*""",
            "humble": """
RUN curl --resolve raw.githubusercontent.com:443:185.199.108.133 -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \\
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null \\
    && apt update \\
    && DEBIAN_FRONTEND=noninteractive apt install -y ros-humble-desktop python3-colcon-common-extensions ros-humble-pcl-ros
"""
        }
        return tmp_dict[ros_version]

    def set_apt():
        return """
RUN sed -i s@/archive.ubuntu.com/@/mirrors.tuna.tsinghua.edu.cn/@g /etc/apt/sources.list \\
    && rm /etc/apt/sources.list.d/* \\
    && apt update \\
    && DEBIAN_FRONTEND=noninteractive apt install -y \\
        apt-utils \\
        bash-completion \\
        build-essential \\
        ca-certificates \\
        cmake \\
        curl \\
        gcc-9 g++-9 gcc-10 g++-10 \\
        git \\
        keyboard-configuration \\
        libboost-all-dev \\
        libfmt-dev \\
        libx11-dev \\
        libyaml-cpp-dev \\
        locales \\
        lsb-core \\
        mlocate \\
        nano \\
        net-tools \\
        openssh-server \\
        python3-dev \\
        python3-empy \\
        python3-pip \\
        software-properties-common \\
        sudo \\
        unzip \\
        vim \\
        wget \\
    && rm -rf /var/lib/apt/lists/*
"""

    def set_nvidia():
        return """
# >>> nvidia-container-runtime >>>
ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics
ENV __NV_PRIME_RENDER_OFFLOAD=1 
ENV __GLX_VENDOR_LIBRARY_NAME=nvidia
"""

    def set_shell():
        return """
SHELL ["/bin/bash", "-c"]
"""

    def set_others():
        tmp_str = ""
        if ubuntu_version == "20.04":
            tmp_str += """# Fix https://github.com/ros-visualization/rviz/issues/1780.
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:beineri/opt-qt-5.12.10-focal -y \\
    && apt update \\
    && apt install -y qt512charts-no-lgpl qt512svg qt512xmlpatterns qt512tools qt512translations qt512graphicaleffects qt512quickcontrols2 qt512wayland qt512websockets qt512serialbus qt512serialport qt512location qt512imageformats qt512script qt512scxml qt512gamepad qt5123d
    
"""
        tmp_str += """# Install hstr
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:ultradvorka/ppa -y \\
    && apt update \\
    && apt update && apt install -y hstr \\
    && rm -rf /var/lib/apt/lists/*
"""
        return tmp_str

    def set_entrypoint():
        return """
ENTRYPOINT ["/bin/bash"]
"""

    def set_user_permissions():
        return """# >>> Change user permissions >>>
ARG USER_NAME=liobench
# Set the password '123' for the 'liobench' user
RUN useradd ${USER_NAME} -m -G sudo -u 1000 -s /bin/bash && echo ${USER_NAME}:123 | chpasswd
USER ${USER_NAME}
"""

    def set_workdir():
        return """WORKDIR /home/${USER_NAME}"""

    def set_bashrc():
        tmp_str = ""
        if ros_version == "noetic":
            tmp_str += 'RUN echo "source /opt/qt512/bin/qt512-env.sh" >> ~/.bashrc'

        tmp_str += f"""
RUN echo "source /opt/ros/{ros_version}/setup.bash" >> ~/.bashrc
"""
        return tmp_str

    def setup_workspace():
        return """
RUN git clone https://github.com/Natsu-Akatsuki/liobench ~/liobench/liobench/src
"""

    def install_dep():
        return """# >>> Install GTSAM, Ceres, Sophus, Livox_SDK>>>
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:borglab/gtsam-release-4.0 -y \
    && apt update \
    && apt install -y libgtsam-dev libgtsam-unstable-dev \
    && cd /tmp \
    && apt install -y libgoogle-glog-dev libgflags-dev libatlas-base-dev libeigen3-dev libsuitesparse-dev \
    && wget -c http://ceres-solver.org/ceres-solver-2.1.0.tar.gz -O /tmp/ceres-solver-2.1.0.tar.gz \
    && cd /tmp \
    && tar -xzvf ceres-solver-2.1.0.tar.gz \
    && cd /tmp/ceres-solver-2.1.0 \
    && mkdir build && cd build && cmake .. \
    && make -j4 \
    && make install \
    && cd /tmp/ \
    && git clone https://github.com/strasdat/Sophus.git -b 1.22.4 --depth=1\
    && cd Sophus \
    && mkdir build && cd build && cmake -DSOPHUS_USE_BASIC_LOGGING=ON -DBUILD_SOPHUS_EXAMPLES=FALSE -DBUILD_SOPHUS_TESTS=FALSE ..  \
    && make install \
    && cd /tmp \
    && git clone https://github.com/Livox-SDK/Livox-SDK.git \
    && cd Livox-SDK/build \
    && cmake .. && make install -j4 \
    && cd /tmp/ \
    && rm -rf /tmp/* \
    && rm -rf /var/lib/apt/lists/*
"""

    target_path = target_dir / "Dockerfile"
    with open(target_path, "w") as f:
        f.write(f"FROM {set_basic_image()}\n")
        f.write(f"{set_apt()}\n")
        f.write(f"{set_ros()}\n")
        f.write(f"{set_nvidia()}\n")
        f.write(f"{set_shell()}\n")
        f.write(f"{set_others()}\n")
        f.write(f"{set_entrypoint()}\n")
        f.write(f"{set_user_permissions()}\n")
        f.write(f"{set_workdir()}\n")
        f.write(f"{set_bashrc()}\n")
        # f.write(f"{setup_workspace()}\n")


def set_docker_compose(prefix):
    return f"""services:
  liobench:
    image: liobench:{prefix}
    container_name: liobench
    volumes:
      # Map host workspace to container workspace (Please change to your own path)      
      - $HOME/liobench:/home/liobench/workspace/:rw
      - $HOME/dataset:/home/liobench/dataset/:rw
      - /tmp/.X11-unix:/tmp/.X11-unix:rw      
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    environment:
      - DISPLAY=$DISPLAY
      - NVIDIA_VISIBLE_DEVICES=all
      - LANG=C.UTF-8 # Fix garbled Chinese text
      - LC_ALL=C.UTF-8
    tty: true
    stdin_open: true
    restart: 'no'
"""


def generate_docker_compose(target_dir, prefix):
    target_path = target_dir / "docker-compose.yml"
    with open(target_path, "w") as f:
        f.write(f"{set_docker_compose(prefix)}")


def set_build_bash(prefix):
    return f"""#!/bin/bash
docker build -t liobench:{prefix} --network=host -f Dockerfile .
"""


def generate_build_bash(target_dir, prefix):
    target_path = target_dir / "build_image.sh"
    with open(target_path, "w") as f:
        f.write(f"{set_build_bash(prefix)}")


def generate_build_image_workflow(prefix):
    template_path = Path(__file__).resolve().parent / "build_image_template.yml"
    with open(template_path, 'r') as file:
        content = file.read()

    content = re.sub(r'\${{ PREFIX }}', prefix, content)
    target_path = Path(__file__).resolve().parent.parent / '.github/workflows' / f"build_image_{prefix}.yml"
    with open(target_path, 'w') as file:
        file.write(content)


def main():
    args = parse_args()

    if 0:
        # {22.04, 20.04}
        ubuntu_version = "20.04"
        # {noetic, humble}
        ros_version = "noetic"
        # {11.1.1, 12.4.1 (require: nvidia-driver 550)}
        cuda_version = "12.1.1"
    else:
        ubuntu_version = args.ubuntu_version
        ros_version = args.ros_version
        cuda_version = args.cuda_version

    target_dir = Path(__file__).resolve().parent
    prefix = f"ubuntu{ubuntu_version}_cuda{cuda_version}_{ros_version}"
    target_dir = target_dir / prefix

    generate_dockerfile(ubuntu_version, ros_version, cuda_version, target_dir)
    generate_docker_compose(target_dir, prefix)
    generate_build_bash(target_dir, prefix)
    generate_build_image_workflow(prefix)


if __name__ == "__main__":
    main()

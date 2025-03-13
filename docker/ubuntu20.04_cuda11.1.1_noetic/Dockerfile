FROM nvidia/cuda:11.1.1-cudnn8-devel-ubuntu20.04

RUN sed -i s@/archive.ubuntu.com/@/mirrors.tuna.tsinghua.edu.cn/@g /etc/apt/sources.list \
    && rm /etc/apt/sources.list.d/* \
    && apt update \
    && DEBIAN_FRONTEND=noninteractive apt install -y \
        apt-utils \
        bash-completion \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        gcc-9 g++-9 gcc-10 g++-10 \
        git \
        keyboard-configuration \
        libboost-all-dev \
        libfmt-dev \
        libx11-dev \
        libyaml-cpp-dev \
        locales \
        lsb-core \
        mlocate \
        nano \
        net-tools \
        openssh-server \
        python3-dev \
        python3-empy \
        python3-pip \
        software-properties-common \
        sudo \
        unzip \
        vim \
        wget \
    && rm -rf /var/lib/apt/lists/*


RUN DEBIAN_FRONTEND=noninteractive sh -c '. /etc/lsb-release && echo "deb http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/ `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list' \
    && apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654 \
    && apt update \
    && DEBIAN_FRONTEND=noninteractive apt install -y ros-noetic-desktop-full \
        python3-catkin-tools \
        python3-rosdep \
        python3-rosinstall \
        python3-rosinstall-generator \
        python3-wstool \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# >>> nvidia-container-runtime >>>
ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics
ENV __NV_PRIME_RENDER_OFFLOAD=1 
ENV __GLX_VENDOR_LIBRARY_NAME=nvidia


SHELL ["/bin/bash", "-c"]

# Fix https://github.com/ros-visualization/rviz/issues/1780.
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:beineri/opt-qt-5.12.10-focal -y \
    && apt update \
    && apt install -y qt512charts-no-lgpl qt512svg qt512xmlpatterns qt512tools qt512translations qt512graphicaleffects qt512quickcontrols2 qt512wayland qt512websockets qt512serialbus qt512serialport qt512location qt512imageformats qt512script qt512scxml qt512gamepad qt5123d
    
# Install hstr
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:ultradvorka/ppa -y \
    && apt update \
    && apt update && apt install -y hstr \
    && rm -rf /var/lib/apt/lists/*


ENTRYPOINT ["/bin/bash"]

# >>> Change user permissions >>>
ARG USER_NAME=liobench
# Set the password '123' for the 'liobench' user
RUN useradd ${USER_NAME} -m -G sudo -u 1000 -s /bin/bash && echo ${USER_NAME}:123 | chpasswd
USER ${USER_NAME}

WORKDIR /home/${USER_NAME}
RUN echo "source /opt/qt512/bin/qt512-env.sh" >> ~/.bashrc
RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc


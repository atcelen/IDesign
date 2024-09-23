ARG PYTORCH="1.13.1"
ARG CUDA="11.6"
ARG CUDNN="8"

FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel

LABEL description="Docker image for IDesign"

# Modify the following environment variables to match your system from the list: 6.0 6.1 6.2 7.0 7.2 7.5 8.0 8.6
ENV TORCH_CUDA_ARCH_LIST="8.6"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV CUDA_HOME=/usr/local/cuda-11.6

RUN apt-get -y update
RUN apt-get -y install git

RUN apt-get update
RUN apt-get install -y git ninja-build cmake build-essential libopenblas-dev \
    xterm xauth openssh-server tmux wget mate-desktop-environment-core

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/atcelen/IDesign.git
WORKDIR IDesign

RUN pip install -r requirements.txt
RUN pip install numpy==1.26.4 flaml==2.1.2
ENV MAX_JOBS=8
RUN git clone --recursive "https://github.com/NVIDIA/MinkowskiEngine"
RUN cd MinkowskiEngine; python setup.py install --force_cuda --blas=openblas

# Copy the "OAI_CONFIG_LIST.json" file
COPY OAI_CONFIG_LIST.json OAI_CONFIG_LIST.json
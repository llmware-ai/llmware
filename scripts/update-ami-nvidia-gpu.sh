#! /bin/bash

# This script updates the llmware 0.1.3 AMI with Cuda and required dependencies to take advantage of Nvidia GPU instances

# Setup cuda keyring so that we just have to run a single 'apt update' below
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
rm cuda-keyring_1.1-1_all.deb

# Install ubuntu + nvidia drivers
sudo apt update
sudo apt install -y ubuntu-drivers-common nvidia-driver-535

# Install cuda
sudo apt install -y cuda

# Update .bashrc and the current shell's environment
echo "export PATH=/usr/local/cuda/bin:${PATH}" >> ~/.bashrc 
echo "export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:${LD_LIBRARY_PATH}" >> ~/.bashrc
source ~/.bashrc

# Base image with Python 3.11
FROM python:3.11-bookworm

# Define build arguments
ARG USERNAME=llmware
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

# Set environment variables
ENV PYTHONPATH=/llmware

# Update and install required packages, optimize by combining the steps
RUN apt-get update && apt-get install -y \
    git \
    bash \
    postgresql \
    musl-dev \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository and install Python package dependencies
RUN git clone https://github.com/llmware-ai/llmware.git /llmware \
    && cd /llmware/llmware \
    && pip install --no-cache-dir -r requirements.txt

# Create a user with specified UID and GID, assign ownership of /llmware
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} \
    && chown -R ${USERNAME}:${USER_GID} /llmware

# Switch to the created user
USER ${USERNAME}

# Set the working directory
WORKDIR /llmware

# Set the default command to run bash
CMD ["/bin/bash"]

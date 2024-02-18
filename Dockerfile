FROM python:3.11-slim-bookworm

ARG USERNAME=llmware
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ENV PYTHONPATH=/llmware


RUN apt-get update \ 
&& apt-get install -y --no-install-recommends git bash \
&& apt-get purge -y --auto-remove

RUN git clone https://github.com/llmware-ai/llmware.git
RUN /llmware/scripts/dev/load_native_libraries.sh
RUN cd llmware/llmware && pip install -r requirements.txt


# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chown -R $USERNAME:$USER_GID /llmware
ENV PYTHONPATH=/llmware
WORKDIR /llmware

CMD /bin/bash

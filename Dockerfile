FROM python:3.11-slim-bookworm
RUN apt-get update \ 
&& apt-get install -y --no-install-recommends git bash \
&& apt-get purge -y --auto-remove

RUN git clone https://github.com/llmware-ai/llmware.git
RUN /llmware/scripts/dev/load_native_libraries.sh
RUN cd llmware/llmware && pip install -r requirements.txt

ENV PYTHONPATH=/llmware
WORKDIR /llmware

CMD /bin/bash

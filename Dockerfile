FROM python:3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils 2>&1 \
    && apt-get -y install git locales gcc g++ sudo procps lsb-release \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=prospector-dev
RUN useradd -m $USERNAME

RUN echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME
RUN chmod 0440 /etc/sudoers.d/$USERNAME

RUN echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config

RUN mkdir -p /workspaces/prospector
RUN chown -Rf 1000:1000 /workspaces/prospector
COPY --chown=1000:1000 . /workspaces/prospector/
ENV HOME /workspaces/prospector
USER $USERNAME
WORKDIR /workspaces/prospector/
RUN sudo python3 -m pip install --no-cache-dir -e .[with_everything]
RUN sudo python3 -m pip install --no-cache-dir pre-commit rope
RUN pre-commit install
ENV DEBIAN_FRONTEND=dialog

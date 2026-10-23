FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm
# The base image includes an unused Yarn feed whose signing key may expire.
RUN rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

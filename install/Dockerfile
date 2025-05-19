# Builder stage
FROM registry.access.redhat.com/ubi8/ubi-minimal AS builder

ARG TARGETARCH

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install OS build dependencies
RUN microdnf upgrade -y && \
    microdnf install -y \
    git \
    openssh-clients \
    gcc \
    gcc-c++ \
    make \
    python3.12-devel \
    openssl-devel \
    bzip2-devel \
    libffi-devel \
    zlib-devel \
    wget \
    findutils \
    && microdnf clean all

# Install Python 3.12 and pip 3.12
RUN microdnf install -y python3.12 python3.12-pip && \
    microdnf clean all

# Create symlink for python3 to point to python3.12
RUN ln -s /usr/bin/python3.12 /usr/local/bin/python && \
    ln -s /usr/bin/pip3.12 /usr/local/bin/pip

# Install uv (and pip for compatibility)
RUN pip install --upgrade pip && \
    pip install "uv==0.7.3"

WORKDIR /application

# Copy dependency files
COPY ./README.md ./pyproject.toml ./uv.lock ./

# Install Python dependencies using uv into .venv
RUN uv sync --all-extras

# Or, if you want only main dependencies (no dev/test):
# RUN uv venv .venv && .venv/bin/uv pip install -r <(uv pip compile pyproject.toml)

# Runtime Stage
FROM registry.access.redhat.com/ubi8/ubi-minimal AS runtime

WORKDIR /application

# Set environment for virtual environment
ENV VIRTUAL_ENV=/application/.venv \
    PATH="/application/.venv/bin:$PATH"

# Copy the virtual environment from the builder
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Enable AppStream repository and install Python and other necessary runtime packages
RUN microdnf upgrade -y && \
    microdnf install -y \
    python3.12 \
    && microdnf clean all

# Create symlink for python3 to point to python3.12
RUN ln -s /usr/bin/python3.12 /usr/local/bin/python

# Copy the rest of the code
COPY . /application

# Set the entrypoint
ENTRYPOINT ["python", "/application/main.py"]

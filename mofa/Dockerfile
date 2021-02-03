# Written by Box-in-a-Box ICT, 2020
# (c) Utrecht University

# Use python 3
FROM python:3

# Set environment
ENV PYTHONUNBUFFERED=1

# Create a directory in the linux container with name "code"
RUN mkdir /code

# Set working directory to "code" directory
WORKDIR /code

# Copy requirements to "code" directory
COPY requirements.txt /code/

# Install all required plugins from requirements.txt using pip3, a python package manager
RUN pip3 install -r requirements.txt

# Copy all python source code files to the "code" directory
COPY . /code/

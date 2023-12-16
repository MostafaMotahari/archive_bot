FROM docker.arvancloud.ir/python:3.11.5-alpine3.18
# Setting working directory
WORKDIR /home/archive_bot
# Adding Static Directory
RUN mkdir docs_repo
# Copying source
COPY telegram .
# Addding requirements
COPY requirements.txt requirements.txt
RUN pip install -U pip && pip install -r requirements.txt --no-cache-dir
# Running
CMD python __main__.py

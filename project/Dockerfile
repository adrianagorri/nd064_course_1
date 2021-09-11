# set the base image
FROM python:2.7
# set a key-value label for the docker image
LABEL maintainer="Adriana Gorri"
# copy files from the host to the container filesystem
COPY ./techtrends /app
# defines the working directory within the container
WORKDIR /app
# execute commands within the container
RUN pip install -r requirements.txt
RUN python init_db.py
# expose an application port
EXPOSE 3111
# set the default command to execute when the container starts
CMD [ "python", "app.py" ]

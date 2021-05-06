FROM python:3.6.13
RUN pip3 install Flask==1.1.2 \
                 hotqueue==0.2.8 \
                 pytest==6.2.3 \
                 redis==3.5.3 \
                 requests==2.25.1 \
                 matplotlib

COPY ./src /app
COPY ./data/newdata.json /app/data/newdata.json

WORKDIR /app

ENTRYPOINT [ "python3" ]

FROM python:3.10
WORKDIR /app
COPY . /app
RUN chmod +x entrypoint.sh
RUN pip3 install -r requirements.txt
CMD ./entrypoint.sh
VOLUME /app/db
EXPOSE 8000
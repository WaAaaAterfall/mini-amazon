FROM python:3
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip3 install -r requirements.txt
RUN pip3 install protobuf
ADD . /code/
RUN chmod o+x runweb.sh
RUN chmod o+x runamazon.sh

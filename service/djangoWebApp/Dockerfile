FROM python:3.5.2
RUN pip install django json2html
EXPOSE 5000
COPY $PWD /usr/src/myapp
WORKDIR /usr/src/myapp
RUN mkdir results

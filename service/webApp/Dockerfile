FROM python:3.5.2
RUN pip install flask json2html requests pyyaml numpy pymongo
EXPOSE 5000
RUN mkdir /root/.kube
COPY $PWD /usr/src/myapp
WORKDIR /usr/src/myapp
RUN mkdir results
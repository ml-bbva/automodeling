FROM python:3.5.2
RUN pip install requests pyyaml numpy
RUN mkdir /root/.kube
COPY $PWD /usr/src/myapp
WORKDIR /usr/src/myapp

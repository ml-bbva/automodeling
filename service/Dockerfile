FROM python:3.5.2
RUN pip install requests pyyaml numpy flask json2html
RUN mkdir /root/.kube
EXPOSE 5000
COPY $PWD /usr/src/myapp
WORKDIR /usr/src/myapp

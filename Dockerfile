FROM python:3.7-alpine
MAINTAINER Daniel Johannessen "daniel.johannessen@sesam.io"
RUN apk add --no-cache cmake gcc libxml2 automake g++ subversion python3-dev libxml2-dev libxslt-dev lapack-dev gfortran
RUN apk update
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python3","-u","service.py"]

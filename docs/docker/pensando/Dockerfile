#     Copyright (c) 2020 World Wide Technology, LLC
#     All rights reserved.
#
#     author: joel.king@wwt.com (@joelwking)
#     written:  20 July 2020
#
#
FROM ubuntu:18.04

MAINTAINER @joelwking

LABEL version="1.0" description="Demo image for Pensando PSM API"
#
# Install software
#
RUN apt-get update && \
    apt-get install -y software-properties-common  && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install git -y && \
    apt-get install python-pip -y && \
    apt-get install python-dev -y  && \
    pip install requests && \
    pip install pyopenssl  && \
    pip install pydevd  && \
    pip install tetpyclient && \
    pip install ansible-lint  && \
    apt-add-repository --yes --update ppa:ansible/ansible  && \
    apt-get install ansible -y

#
#  Configure directory structure
#
ENV ANSIBLE_COLLECTIONS_PATHS=/collections/
RUN mkdir -p /collections/ansible_collections/joelwking/
WORKDIR /collections/ansible_collections/joelwking/
#
#   For now, clone the repository, TODO use ansible-galaxy
#
RUN git clone https://github.com/joelwking/pensando.git
#
#   Install any necessary Tetration custom modules
#
ADD  https://raw.githubusercontent.com/joelwking/ansible-tetration/master/library/tetration_application.py /collections/ansible_collections/joelwking/pensando/playbooks/library/tetration_application.py

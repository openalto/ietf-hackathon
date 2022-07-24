FROM centos:7

COPY dmc.repo /etc/yum.repos.d/dmc.repo
ADD fts.spec /

RUN yum groupinstall -y 'Development Tools'
RUN yum install -y epel-release yum-utils git
RUN yum-builddep -y "/fts.spec"
RUN yum install -y gfal2-all jsoncpp-devel
RUN yum clean all

FROM rucio/xrootd

RUN yum -y install net-tools iproute && \
    yum clean all && \
    rm -rf /var/cache/yum

RUN yum -y install vim

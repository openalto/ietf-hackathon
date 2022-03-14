FROM rucio/rucio-dev:py3

RUN ln -fs /usr/bin/python2 /usr/bin/python && \
    yum -y install net-tools iproute && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    ln -fs /usr/bin/python3 /usr/bin/python

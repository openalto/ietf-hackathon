FROM ubuntu:20.04
LABEL org.opencontainers.image.authors="David Bainbridge <dbainbri@ciena.com>,Jensen Zhang <hack@jensen-zhang.site>"

ENV DEBIAN_FRONTEND noninteractive

ENV MININET_REPO git://github.com/mininet/mininet
ENV MININET_INSTALLER ./mininet/util/install.sh
ENV INSTALLER_SWITCHES -fbinptvwyx
ENV G2_MININET_REPO git://github.com/reservoirlabs/g2-mininet
ENV MININET_SRC /opt/mininet
ENV G2_MININET_SRC /opt/mininet/g2-mininet

WORKDIR /opt

# Update and install minimal.
RUN \
    apt-get update \
        --quiet \
    && apt-get install \
        --yes \
        --no-install-recommends \
        --no-install-suggests \
    autoconf \
    automake \
    ca-certificates \
    git \
    curl \
    libtool \
    net-tools \
    iputils-ping \
    iperf3 \
    tcpdump \
    openssh-client \
    xterm \
    patch \
    vim \

# Clone and install mininet.
    && git clone -b 2.3.0 $MININET_REPO \

# A few changes to make the install script behave.
    && sed -e 's/sudo //g' \
    	-e 's/~\//\//g' \
    	-e 's/\(apt-get -y install\)/\1 --no-install-recommends --no-install-suggests/g' \
    	-i $MININET_INSTALLER \

# Install script expects to find this. Easier than patching that part of the script.
    && touch /.bashrc \

# Proceed with the install.
    && chmod +x $MININET_INSTALLER \
    && ./$MININET_INSTALLER $INSTALLER_SWITCHES \

# Link ovs-tsetcontroller to ovs-controller
    && ln -s /usr/bin/ovs-testcontroller /usr/bin/ovs-controller \

# Clone and install g2-mininet.
    && cd $MININET_SRC \
    && git clone $G2_MININET_REPO \
    && cp g2-mininet/pox/g2_static.py $MININET_SRC/pox/ext/ \

# Clean up packages.
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a start script to start OpenVSwitch
COPY docker-entry-point /docker-entry-point
RUN chmod 755 /docker-entry-point

VOLUME ["/etc/g2-mininet"]
WORKDIR /etc/g2-mininet

# Default command.
ENTRYPOINT ["/docker-entry-point"]

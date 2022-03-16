FROM containernet/containernet:latest
LABEL org.opencontainers.image.authors="Jensen Zhang <hack@jensen-zhang.site>"

ENV MININET_INSTALLER util/install.sh
ENV INSTALLER_SWITCHES -p
ENV G2_MININET_REPO https://github.com/reservoirlabs/g2-mininet.git
ENV MININET_SRC /containernet
ENV G2_MININET_SRC /containernet/g2-mininet

# Update and install minimal.
RUN \
    $MININET_INSTALLER $INSTALLER_SWITCHES \
    && git clone $G2_MININET_REPO \
    && cp g2-mininet/pox/g2_static.py $MININET_SRC/pox/ext/

# Create a start script to start OpenVSwitch
COPY docker-entry-point /docker-entry-point
RUN chmod 755 /docker-entry-point

VOLUME ["/etc/g2-mininet"]

# Default command.
ENTRYPOINT ["/docker-entry-point"]

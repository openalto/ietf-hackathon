FROM bitnami/java:1.8
LABEL org.opencontainers.image.authors="Jensen Zhang <hack@jensen-zhang.site>"

ENV ODL_VERSION 0.8.4
ENV PATCH_VERSION patch%2Fbgp-3.5

# Install OpenDaylight
RUN \
    apt-get update --quiet \
    && apt-get install -y --no-install-recommends unzip \
    && wget -O karaf-$ODL_VERSION.tar.gz https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/karaf/$ODL_VERSION/karaf-$ODL_VERSION.tar.gz \
    && tar xvf karaf-$ODL_VERSION.tar.gz -C /opt \
    && mv /opt/karaf-$ODL_VERSION /opt/opendaylight \

# Install ALTO patch
    && wget -O odl-alto-patch.zip https://github.com/openalto/sextant/releases/download/$PATCH_VERSION/odl-alto-patch.zip \
    && unzip odl-alto-patch.zip \
    && odl-alto-patch/install_patch.sh /opt/opendaylight \

# Cleanup packages
    && apt-get clean \
    && rm karaf-$ODL_VERSION.tar.gz odl-alto-patch.zip \
    && rm -rf odl-alto-patch \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8181
EXPOSE 8080
EXPOSE 6633
EXPOSE 6653

ENTRYPOINT [ "/opt/opendaylight/bin/start" ]

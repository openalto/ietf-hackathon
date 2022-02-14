FROM bitnami/java:1.8
LABEL org.opencontainers.image.authors="Jensen Zhang <hack@jensen-zhang.site>"

ENV ODL_VERSION 0.6.4-Carbon
ENV PATCH_VERSION patch%2Fbgp-3.5

# Install OpenDaylight
RUN \
    curl -sSLO https://nexus.opendaylight.org/content/groups/public/org/opendaylight/integration/distribution-karaf/$ODL_VERSION/distribution-karaf-$ODL_VERSION.tar.gz \
    && tar xvf distribution-karaf-$ODL_VERSION.tar.gz -C /opt \
    && mv /opt/distribution-karaf-$ODL_VERSION /opt/opendaylight \

# Install ALTO patch
    && curl -sSLO https://github.com/openalto/sextant/releases/download/$PATCH_VERSION/odl-alto-patch.zip \
    && unzip odl-alto-patch.zip \
    && odl-alto-patch/install_patch.sh /opt/opendaylight \

# Cleanup packages
    && rm distribution-karaf-$ODL_VERSION.tar.gz odl-alto-patch.zip \
    && rm -rf odl-alto-patch

EXPOSE 8080
EXPOSE 6633
EXPOSE 6653

ENTRYPOINT [ "/opt/opendaylight/bin/karaf" ]

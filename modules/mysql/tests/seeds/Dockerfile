#
# custom mysql image
#
ARG MYSQL_VERSION="8.0"
FROM mysql:${MYSQL_VERSION} as builder

# That file does the DB initialization but also runs mysql daemon, by removing the last line it will only init
RUN ["sed", "-i", "s/exec \"$@\"/echo \"not running $@\"/", "/usr/local/bin/docker-entrypoint.sh"]

# needed for intialization
ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=test MYSQL_USER=test MYSQL_PASSWORD=test

COPY *.sql /docker-entrypoint-initdb.d/

# Need to change the datadir to something other than /var/lib/mysql because the parent docker file defines it as a volume.
# https://docs.docker.com/engine/reference/builder/#volume :
#       Changing the volume from within the Dockerfile: If any build steps change the data within the volume after
#       it has been declared, those changes will be discarded.
RUN ["/usr/local/bin/docker-entrypoint.sh", "mysqld", "--datadir", "/initialized-db" ]

#
# create final container
#
FROM mysql:${MYSQL_VERSION}

# copy datadir from builder
COPY --from=builder /initialized-db /var/lib/mysql

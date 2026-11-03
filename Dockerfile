FROM eclipse-temurin:25-jre

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/practice
COPY manifest.txt versions.lock setup.sh start.sh ./
COPY defaults ./defaults
COPY docker/entrypoint.sh ./docker/entrypoint.sh

# server/ is a volume so worlds, configs and player data survive rebuilds
VOLUME /opt/practice/server
EXPOSE 25565

ENTRYPOINT ["./docker/entrypoint.sh"]

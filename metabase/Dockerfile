FROM openjdk:11

COPY metabase.jar ./metabase.jar

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

EXPOSE 8080

CMD java -Xmx1000m -jar ./metabase.jar
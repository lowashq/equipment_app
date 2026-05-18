FROM clojure:lein-2.11.2

WORKDIR /app

COPY project.clj .
RUN lein deps

COPY . .
RUN lein uberjar

EXPOSE 3001

CMD ["java", "-jar", "target/decision-engine-1.0.0-standalone.jar"]

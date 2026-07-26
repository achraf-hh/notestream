# Build stage: compile and package the Spring Boot fat jar with the Gradle wrapper.
FROM eclipse-temurin:21-jdk AS build
WORKDIR /app

# Copy build scripts + wrapper first so dependency resolution is cached across source-only changes.
COPY gradlew settings.gradle.kts build.gradle.kts ./
COPY gradle ./gradle
RUN ./gradlew --no-daemon dependencies || true

COPY src ./src
RUN ./gradlew --no-daemon clean bootJar

# Runtime stage: JRE only, no build tooling.
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/build/libs/*-SNAPSHOT.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]

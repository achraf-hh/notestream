plugins {
	java
	id("org.springframework.boot") version "3.4.11"
	id("io.spring.dependency-management") version "1.1.7"
}

group = "com.notestream"
version = "0.0.1-SNAPSHOT"
description = "Demo project for Spring Boot"

java {
	toolchain {
		languageVersion = JavaLanguageVersion.of(21)
	}
}

configurations {
	compileOnly {
		extendsFrom(configurations.annotationProcessor.get())
	}
}

repositories {
	mavenCentral()
}

// Spring Boot 3.4 manages Testcontainers 1.20.x, which can't connect to Docker Engine 29
// ("Could not find a valid Docker environment"). 1.21.4 can.
extra["testcontainers.version"] = "1.21.4"

dependencies {
	implementation("org.springframework.boot:spring-boot-starter-actuator")
	implementation("org.springframework.boot:spring-boot-starter-data-jpa")
	implementation("org.springframework.boot:spring-boot-starter-validation")
	implementation("org.springframework.boot:spring-boot-starter-web")
	compileOnly("org.projectlombok:lombok")
	runtimeOnly("org.postgresql:postgresql")
	annotationProcessor("org.projectlombok:lombok")
	testImplementation("org.springframework.boot:spring-boot-starter-test")
	testImplementation("org.springframework.boot:spring-boot-testcontainers")
	testImplementation("org.testcontainers:junit-jupiter")
	testImplementation("org.testcontainers:postgresql")
	testRuntimeOnly("org.junit.platform:junit-platform-launcher")
	implementation("org.hibernate.orm:hibernate-vector:6.6.11.Final")
	implementation("org.apache.pdfbox:pdfbox:3.0.3")
	implementation("org.flywaydb:flyway-core")
	implementation("org.flywaydb:flyway-database-postgresql")
}

tasks.withType<Test> {
	useJUnitPlatform()
}

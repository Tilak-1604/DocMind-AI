# DocMind-AI Backend

This is a Spring Boot application.

## Prerequisites

- **Java**: Java 21 is required.
- **Maven**: Ensure you have Maven installed on your system to build and run the project (since the `mvnw` shell script is not present, you will need to use your system's `mvn` command).
- **MySQL**: The project includes a MySQL connector, so you'll need a MySQL database running.
- **Kafka**: The project has Kafka dependencies, so you'll need a Kafka broker running for messaging features.

## How to run

1. **Configure Properties**: Before running, ensure you have an `application.properties` or `application.yml` file in `src/main/resources/` with the appropriate database and Kafka connection details.

2. **Run the application**: Navigate to the `Backend` directory and execute the following command:
   ```bash
   mvn spring-boot:run
   ```

3. **Build a JAR**: If you want to package the application into a JAR file, run:
   ```bash
   mvn clean install
   ```
   After building, you can run the generated JAR from the `target` directory:
   ```bash
   java -jar target/docmindAI-0.0.1-SNAPSHOT.jar
   ```

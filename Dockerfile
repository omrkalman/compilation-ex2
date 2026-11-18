
# Use a Linux image with Java 17
FROM eclipse-temurin:17-jdk

# Install build tools
RUN apt-get update && apt-get install -y \
    make \
    jflex \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /project

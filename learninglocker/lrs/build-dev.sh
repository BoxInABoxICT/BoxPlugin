# Build the docker images
docker build -t fundocker/learninglocker:v2.6.2 --build-arg LL_VERSION="v2.6.2" ./learninglocker/
docker build -t fundocker/xapi-service:v2.2.15 --build-arg VERSION="v2.2.15" ./xapi/

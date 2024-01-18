set -ex

# export HOST_USER=dev
# export HOST_UID=$(id -u)
# export HOST_GID=$(id -g)
cd $(dirname $0)
cd ".."
# cp ~/.ssh/id_rsa.pub .
# cp ../.env.sh .
#docker build --build-arg HOST_USER=dev --build-arg HOST_UID=$HOST_UID --build-arg HOST_GID=$HOST_GID . -t portal-backend/app:local
docker build . -t hackernews/app:local
docker save hackernews/app > /tmp/image.tar
[[ "$(uname)" == "Darwin" ]] && multipass transfer /tmp/image.tar microk8s-vm:/tmp/image.tar
microk8s ctr image import /tmp/image.tar
rm /tmp/image.tar
# rm ./id_rsa.pub
# rm ./.env.sh
set -ex

cd $(dirname $0)
cd ".."
docker build . -t hackernews/app:local
docker save hackernews/app > /tmp/image.tar
[[ "$(uname)" == "Darwin" ]] && multipass transfer /tmp/image.tar microk8s-vm:/tmp/image.tar
microk8s ctr image import /tmp/image.tar
rm /tmp/image.tar

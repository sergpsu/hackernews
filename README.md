# hackernews
You can play with it both at localhost and in microk8s deployment.

## run locally
Requires installed prerequisites: ```pip3 install -r ./requirements.txt```
```make run```

## run tests
Requires installed prerequisites: ```pip3 install -r ./requirements_test.txt```
```make test```

## build docker image
```make build```

## deploy into microk8s
Requires built image
```make deploy```

## redeploy into microk8s
Requires docker image to be built aleady
```make redeploy```

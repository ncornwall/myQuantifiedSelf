init:
	pip3 install -r requirements.txt

run:
	python3 my_quantified_self/main.py

test:
	pytest tests

docker-run:
    docker build \
      --file=./Dockerfile \
      --tag=my_project ./
    docker run \
      --detach=false \
      --name=my_project \
      --publish=$(HOST):8080 \
      my_project
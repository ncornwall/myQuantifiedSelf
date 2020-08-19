init:
	pip3 install -r requirements.txt

run:
	python3 my_quantified_self/main.py

test:
	pytest tests

# interactive mode is important as we expect some user input
docker-run:
	docker run -it my_quantified_self:latest

docker-build:
	docker build -t my_quantified_self:latest .

init:
	pip3 install -r requirements.txt

run:
	python3 my_quantified_self/main.py

test:
	pytest tests

docker-run:
	docker run -t my_quantified_self:latest --detach=false

docker-build:
	docker build -t my_quantified_self:latest .

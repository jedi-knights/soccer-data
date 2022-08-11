.PHONY: env cov style start deps install build develop test

.DEFAULT_GOAL := build

env:
	rm -rf env
	python3 -m venv env

clean:
	rm -rf .eggs
	rm -rf *.egg-info
	rm -rf build

install: clean
	@python -m pip install build
	@python -m pip install --upgrade pip
	@python -m pip install --upgrade wheel

build:
	@python -m pip install --editable .

package:
	@python -m build --wheel

lint:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

docker-clean:
	@docker system prune --volumes -f

run: build
	@docker run -p 8080:8080 ocrosby/soccer-data

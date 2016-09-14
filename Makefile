init:
	pip install -r requirements.txt

build: 
	python setup.py build


install: 
	python setup.py install

test:
	nosetests tests

.PHONY: help install clean_install clean_pyc test_database test_database_check run

help:
	@echo "install - create virtualenv and install required modules"
	@echo "clean_install - remove virtualenv and artifacts reltated to package install"

install:
	virtualenv -p /usr/bin/python2.7 venv
	source venv/bin/activate
	pip install -r requirements.txt

clean_install:
	deactivate
	rm -rf venv
	rm -r dist/
	rm -r *.egg-info/
        
clean-pyc: 
	find . -name '*.pyc' -exec rm -f {} + 
	find . -name '*.pyo' -exec rm -f {} + 
	find . -name '*~' -exec rm -f {} + 
	find . -name '__pycache__' -exec rm -fr {} + 

test_database:
	python test/test_database.py > makeCheckDatabase
	
test_database_check:
	python test/test_database_check.py

run:
	python apps/lims_downloader.py > makeRunCheck.txt
	
	

python2.7_path=/usr/bin/python2.7

.PHONY: help install clean_install clean_pyc test_database test_database_check run

help:
    @echo "install - create virtualenv and install required modules"
    @echo "clean_install - remove virtualenv and artifacts reltated to package install"

install:
	virtualenv -p /usr/bin/python2.7 venv
	source venv/bin/activate
        pip install -r requirements.txt
        (or pip setup.py install)

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
	python test_database.py
	
test_database_check:
	python test_database_check.py

run:
	python lims_downloader.py
	
	

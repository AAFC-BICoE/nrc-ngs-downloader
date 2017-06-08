
.PHONY: help install clean_install clean_pyc test_database test_database_check run

help:
	@echo "install - create virtualenv and install required modules"
	@echo "clean_install - remove virtualenv and artifacts reltated to package install"

install:
	#pip install (pypi or github.git#egg = NRC-LIMS-dataDownloader)
	#git clone http://www.github.com/aafc-mbb/NRC-LIMS-dataDownloader.git
	virtualenv -p /usr/bin/python2.7 venv
	#source venv/bin/activate
	venv/bin/pip install nrc_ngs_dl
	
setup_dev:
	virtualenv -p /usr/bin/python2.7 venv
	#source venv/bin/activate
	venv/bin/pip install -r requirements.txt

clean_install:
	#deactivate
	find . -name 'venv' -exec rm -rf {}
	find . -name 'dist/' -exec rm -r {}
	find . -name '*.egg-info/' -exec rm -r {}
        
clean_pyc: 
	find . -name '*.pyc' -exec rm -f {} + 
	find . -name '*.pyo' -exec rm -f {} + 
	find . -name '*~' -exec rm -f {} + 
	find . -name '__pycache__' -exec rm -fr {} + 

test_database:
	python test/test_database.py -c config.ini.sample
	
test_database_check:
	python test/test_database_check.py -c config.ini.sample
	
test_rename:
	python test/test_rename.py -c config.ini.sample

run:
	python nrc_ngs_dl/lims_downloader.py -c config.ini.sample
	
	

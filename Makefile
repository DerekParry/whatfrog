create:
	rm -rf 've'
	python3 -m venv 've'
	ve/bin/pip install --upgrade pip
	ve/bin/pip install --requirement 'requirements.txt'

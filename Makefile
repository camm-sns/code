prefix := /usr/local/camm

all:
	@echo "Run make install to install the CAMM software"
	
check:
	# Check dependencies
	@python -c "import stomp" || echo "\nERROR: stomp.py is not installed: http://code.google.com/p/stomppy\n"
	@python -c "import sns_utilities" || echo "\nERROR sns_utilities is not installed"
	# Done checking dependencies
	
install: check camm

amq:
	# Install AMQ python package
	python setup.py clean
	python setup.py install
	     
camm: amq
	# Make sure the install directories exist
	test -d $(prefix) || mkdir -m 0755 -p $(prefix)
	
	# Install application code
	cp -R * $(prefix)
	
.PHONY: check
.PHONY: install
.PHONY: amq
.PHONY: camm

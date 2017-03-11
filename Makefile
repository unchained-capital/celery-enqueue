#
# == Commands ==
#
PIP  := pip

#
# == Top-Level Targets ==
#
default: dependencies

dependencies: python-dependencies

clean:
	$(FIND) . -iname '*.pyc' -delete

install:
	pip install -e .

uninstall:
	pip uninstall celery-enqueue


#
# == Dependencies ==
#

python-dependencies:
	$(PIP) install -r requirements.txt

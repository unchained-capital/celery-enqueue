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

#
# == Dependencies ==
#

python-dependencies:
	$(PIP) install -r requirements.txt

#
# == Commands ==
#
PYTHON  := python
PIP     := pip
TWINE   := twine
FIND    := find

#
# == Top-Level Targets ==
#

default: dependencies

dependencies:
	$(PIP) install -r requirements.txt

clean:
	$(FIND) . -iname '*.pyc' -delete
	$(RM) -r dist build celery_enqueue.egg-info

install:
	$(PIP) install -e .

uninstall:
	$(PIP) uninstall celery-enqueue

package:
	$(PYTHON) setup.py egg_info
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel --universal

release:
	$(TWINE) upload dist/*

#
# == Dependencies ==
#

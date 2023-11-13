VENV_NAME=.venv
PYTHON=${VENV_NAME}/bin/python3
PIP=${VENV_NAME}/bin/pip

.PHONY: venv
venv:
	if [ ! -d "${VENV_NAME}" ]; then python3 -m venv ${VENV_NAME}; fi

.PHONY: install
install: venv
	${PIP} install -r requirements.txt && \
	${PIP} install pytest

.PHONY: test
test: install
	${VENV_NAME}/bin/pytest

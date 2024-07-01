.PHONY: deps
deps:
		pip install -r requirements.txt && npm i \
			&& git submodule init && git submodule update \
			&& cd sneat-bootstrap-html-admin-template-free && npm i

.DEFAULT_GOAL := deps

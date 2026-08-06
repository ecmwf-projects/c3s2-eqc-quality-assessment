PRE_BUILD_DIR := _pre_build
PRE_BUILD_TMPDIR := $(shell mktemp -d)
PRE_BUILD_FLAGS := "--no-disclaimer"
UNWANTED_DIR := __MACOSX


.PHONY: help qa clean-book pre-build-book build-book

.DEFAULT_GOAL := help

help: ## Show this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

qa: ## Run code quality tools
	pre-commit run --all-files

clean-book: ## Remove temporary build directory
	rm -fr $(PRE_BUILD_DIR)

pre-build-book: clean-book ## Prepare temporary files and run pre-build script
	cp -r * $(PRE_BUILD_TMPDIR)
	rm -fr $(PRE_BUILD_TMPDIR)/$(UNWANTED_DIR)
	mv $(PRE_BUILD_TMPDIR) $(PRE_BUILD_DIR)
	python scripts/pre-build.py $(PRE_BUILD_DIR) $(PRE_BUILD_FLAGS)

build-book: pre-build-book ## Build the Jupyter Book
	jupyter-book build -W -n --keep-going $(PRE_BUILD_DIR)

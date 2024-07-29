PRE_BUILD_DIR := _pre_build
PRE_BUILD_TMPDIR := $(shell mktemp -d)
PRE_BUILD_FLAGS := "--no-disclaimer"

qa:
	pre-commit run --all-files

clean-book:
	rm -fr $(PRE_BUILD_DIR)

pre-build-book: clean-book
	cp -r * $(PRE_BUILD_TMPDIR)
	mv $(PRE_BUILD_TMPDIR) $(PRE_BUILD_DIR)
	python scripts/pre-build.py $(PRE_BUILD_DIR) $(PRE_BUILD_FLAGS)

build-book: pre-build-book
	jupyter-book build -W -n --keep-going $(PRE_BUILD_DIR)

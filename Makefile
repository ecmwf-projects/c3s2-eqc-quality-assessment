PRE_BUILD_DIR := _pre_build
PRE_BUILD_TMPDIR := $(shell mktemp -d)
PRE_BUILD_FLAGS := "--no-disclaimer"
UNWANTED_DIR := __MACOSX


qa:
	pre-commit run --all-files
	git fetch origin main
	pre-commit run -c .pre-commit-config-weekly.yaml --from-ref origin/main --to-ref HEAD

clean-book:
	rm -fr $(PRE_BUILD_DIR)

pre-build-book: clean-book
	cp -r * $(PRE_BUILD_TMPDIR)
	rm -fr $(PRE_BUILD_TMPDIR)/$(UNWANTED_DIR)
	mv $(PRE_BUILD_TMPDIR) $(PRE_BUILD_DIR)
	python scripts/pre-build.py $(PRE_BUILD_DIR) $(PRE_BUILD_FLAGS)

build-book: pre-build-book
	jupyter-book build -W -n --keep-going $(PRE_BUILD_DIR)

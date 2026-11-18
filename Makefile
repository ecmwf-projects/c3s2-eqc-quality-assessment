PRE_BUILD_DIR := _pre_build
PRE_BUILD_FLAGS := "--no-disclaimer"
UNWANTED_DIR := __MACOSX

# Keep the tooling out of .venv, which may hold a notebook development environment
export UV_PROJECT_ENVIRONMENT ?= .venv-tools


.PHONY: help qa qa-all clean-book pre-build-book build-book preview-book stop-preview-book

.DEFAULT_GOAL := help

help: ## Show this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

qa: ## Run code quality tools
	uv run pre-commit run --all-files
	uv run pre-commit run --hook-stage manual --from-ref origin/main --to-ref HEAD

qa-all: ## Run code quality tools on all files
	uv run pre-commit run --all-files --hook-stage manual

clean-book: ## Remove temporary build directory
	rm -fr $(PRE_BUILD_DIR)

pre-build-book: clean-book ## Prepare temporary files and run pre-build script
	tmpdir=$$(mktemp -d) && cp -r * "$$tmpdir" && rm -fr "$$tmpdir/$(UNWANTED_DIR)" && mv "$$tmpdir" $(PRE_BUILD_DIR)
	uv run --group book python scripts/pre-build.py $(PRE_BUILD_DIR) $(PRE_BUILD_FLAGS)

build-book: pre-build-book ## Build the Jupyter Book
	cd $(PRE_BUILD_DIR) && uv run --project $(CURDIR) --group book jupyter-book build --html --strict
	uv run python scripts/post-build.py $(PRE_BUILD_DIR)/_build/html

preview-book: ## Start the preview server in the background
	@if [ -f .book-preview.pid ] && kill -0 $$(cat .book-preview.pid) 2>/dev/null; then \
		echo "Preview server is already running at http://localhost:8000"; \
	else \
		nohup python3 -m http.server 8000 \
			--directory "$(CURDIR)/$(PRE_BUILD_DIR)/_build/html" \
			> /tmp/jupyter-book-preview.log 2>&1 < /dev/null & \
		echo $$! > .book-preview.pid; \
		echo "Preview available at http://localhost:8000"; \
	fi

stop-preview-book: ## Stop the preview server
	@if [ -f .book-preview.pid ]; then \
		kill $$(cat .book-preview.pid) 2>/dev/null || true; \
		rm -f .book-preview.pid; \
		echo "Preview server stopped."; \
	else \
		echo "No preview server running."; \
	fi

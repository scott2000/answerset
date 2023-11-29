PYTHON = python

SOURCE_FILES = src/__init__.py src/config.json src/config.md
OUTPUT_FILE = answerset.ankiaddon

CACHE_DIRS = src/__pycache__ test/__pycache__ .pytest_cache
INSTALL_DIR = ~/Library/'Application Support'/Anki2

.PHONY: build test clean install

build: clean test $(OUTPUT_FILE)

install: $(SOURCE_FILES)
	ln -f $^ $(INSTALL_DIR)/addons21/answerset/

clean:
	rm -rf $(CACHE_DIRS) $(OUTPUT_FILE)

test:
	$(PYTHON) -m pytest -vv

$(OUTPUT_FILE): $(SOURCE_FILES)
	zip -j $@ $^

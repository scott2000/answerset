PYTHON = python

SOURCE_FILES = src/__init__.py src/config.json src/config.md
OUTPUT_FILE = answerset.ankiaddon
TEST_REPORT_FILE = pytest-junit.xml

GENERATED_FILES = $(TEST_REPORT_FILE) $(OUTPUT_FILE)
CACHE_DIRS = src/__pycache__ test/__pycache__ .pytest_cache
INSTALL_DIR = ~/Library/'Application Support'/Anki2

.PHONY: build test clean install

build: clean test $(OUTPUT_FILE)

install: $(SOURCE_FILES)
	ln -f $^ $(INSTALL_DIR)/addons21/answerset/

clean:
	rm -rf $(CACHE_DIRS) $(GENERATED_FILES)

test:
	$(PYTHON) -m pytest -vv --junitxml=$(TEST_REPORT_FILE)

$(OUTPUT_FILE): $(SOURCE_FILES)
	zip -j $@ $^

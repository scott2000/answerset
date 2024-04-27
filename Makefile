SOURCE_FILES = $(wildcard answerset/*.py) answerset/config.json answerset/config.md
OUTPUT_FILE = answerset.ankiaddon
TEST_REPORT_FILE = pytest-junit.xml

GENERATED_FILES = $(TEST_REPORT_FILE) $(OUTPUT_FILE)
CACHE_DIRS = answerset/__pycache__ test/__pycache__ .pytest_cache .mypy_cache .coverage
INSTALL_DIR = ~/Library/'Application Support'/Anki2/addons21/answerset

COVERAGE_FLAGS = --cov=answerset --cov-fail-under=90 --cov-report=term-missing

build: clean test $(OUTPUT_FILE)

install: $(SOURCE_FILES)
	[ -d $(INSTALL_DIR) ] || mkdir $(INSTALL_DIR)
	ln -f $^ $(INSTALL_DIR)

uninstall:
	rm -rf $(INSTALL_DIR)

clean:
	rm -rf $(CACHE_DIRS) $(GENERATED_FILES)

test: check
	pytest --junitxml=$(TEST_REPORT_FILE) $(COVERAGE_FLAGS)

check:
	mypy -p answerset -p test --strict

$(OUTPUT_FILE): $(SOURCE_FILES)
	zip -j $@ $^

.PHONY: build install uninstall clean test check

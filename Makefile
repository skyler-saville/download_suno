# Variables
PYTHON = python
PIP = pip

# Targets
.PHONY: all install run update-deps clean

# Default target
all: run

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Run the main script
run:
	$(PYTHON) main.py

# Update dependencies
update-deps:
	$(PIP) freeze > requirements.txt

# Clean up the project (e.g., remove pyc files or logs)
clean:
	rm -f *.pyc
	rm -f song_data.txt

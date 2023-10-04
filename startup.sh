sudo apt update -y && sudo apt upgrade -y
python3 -m venv venv && pip install --no-cache-dir poetry \
&& poetry config virtualenvs.in-project true && poetry install
pre-commit install

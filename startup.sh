# Chạy file này khi clone repo về lần đầu
# Nếu k chạy được script thì chạy lệnh sudo chmod +x ./*.sh

sudo apt update -y && sudo apt upgrade -y
curl -sSL https://install.python-poetry.org | python3 -
poetry config virtualenvs.in-project true
poetry install
source .venv/bin/activate
pre-commit install
pre-commit run --all-files

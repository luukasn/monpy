if [ ! -d ".venv" ]; then
    echo "Python virtual environment not found, creating one to .venv/"
    python -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

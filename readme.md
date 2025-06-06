## finds s&p stocks that are near their 52 week lows

i would probably run this in a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

or windows
```powerShell
python -m venv venv
venv\Scripts\activate
```

then install the requirements
```bash
pip install yfinance
```

then run the script
```bash
python 52lows.py
```
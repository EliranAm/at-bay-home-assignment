# At-Bay Home Assignment

At-Bay Home Assignment - dispatching cyber scans system.

## Installation

Use Python 3.7

Use pip 20.1.1 

Install requirements.txt

## Usage

Run ingest flask app on local host
```bash
export FLASK_APP=atbay.src.ingest 
flask run -p 4000 
```

Run status flask app on local host
```bash
export FLASK_APP=atbay.src.status 
flask run -p 3000 
```

Run unittest 
```bash
python3 -m atbay.tests.test_process
```

# Oracle APEX export

```
A simple Oracle APEX export utility(CLI based)
Is based on https://oracle-base.com/articles/misc/apexexport
```

## Install requirements
```
1. Download APEX software(based on you're app version) and unzip in the project root as 'apex'
        https://www.oracle.com/tools/downloads/apex-v191-downloads.html
2. Create a virtualenv
        py -m venv venv
3. Install dependencies:
        venv\Scripts\activate
        pip install -r requirements.txt
4. Create a .env file based on .env_example
```

## Run
```
python main.py
```
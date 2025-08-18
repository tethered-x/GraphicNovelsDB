# GraphicNovelsDB
A Python program that maintains a catalog for my graphic novel collection. It utilizes MySQL, CSV, and Python 3.

Requirements:
- Python 3
- MySQL

Installation (from WINDOWS)
- Install MySQL
- Create a username and password for the program to use
- Install Python 3 (I used 3.12)
- Create a Python Virtual Environment
- Activate environment
- Run the following within the venv:
```
    python .\pip_install_script.py
    python .\sql_install_script.py
```
- Execute main program:
```
    python .\main.py
```


KNOWN LIMITATION:
The code doesn't check against provided values to see if UPC matches something or ID matches something
It will just say that the operation is completed but doesn't actually do anything. 
I'll likely build this functionality later.

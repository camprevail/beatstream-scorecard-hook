call venv\Scripts\activate.bat
pyinstaller --version-file=version.py -i slash-icon-hd.ico -F bst-scorecard-hook.py
cmd /k
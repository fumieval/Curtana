def history():
    import readline
    import os
    import atexit

    HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".python_history")
    try:
        readline.read_history_file(HISTORY_FILE)
    except IOError:
        pass

    atexit.register(readline.write_history_file, HISTORY_FILE)
 
def run(*fs):
    for f in fs:
        f()

import os
import curtana.path as PATH

HOME = os.environ["HOME"]
MYCURTANA = os.path.join(HOME, ".curtana")
if __name__ == "__main__":
    os.mkdir(PATH.CURTANA)
    os.touch(PATH.RC)
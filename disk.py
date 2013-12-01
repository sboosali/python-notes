import glob
import os


def get_dropbox_files():
    files = '~/Dropbox/*.note'
    files = glob.glob(os.path.expanduser(files))
    files += [os.path.expanduser('~/Dropbox/.note')]
    return files

def make_files(files):
    return files if files else get_dropbox_files()

def read_files(files):
    files = make_files(files)
    for file in files:
        yield file, open(file).read()

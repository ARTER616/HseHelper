import requests
import traceback as trcb
import os, glob


def list_full_path(path):
    try:
        files = ""
        for filename in glob.iglob(f"{path}/" + '*/', recursive=False):
            #print(filename)
            files = files + f"`{str('/'.join(filename.split('/')[2:]))[:-1]}`\n"
        return files
    except Exception as e:
        print("cfg err: ", e)


def list_full_dir(path):
    try:
        files = ""
        for filename in glob.iglob(f"{path}/" + '*/', recursive=False):
            #print(filename)
            files = files + f"`{str('/'.join(filename.split('/')[1:]))[:-1]}`\n"
        return files
    except Exception as e:
        print("cfg err: ", e)


def list_full_files(path):
    try:
        files = ""
        for filename in glob.iglob(f"{path}/" + '*.*', recursive=False):
            #print(filename)
            #print('/'.join(filename.split('/')[2:]))
            files = files + f"`{'/'.join(filename.split('/')[3:])}`\n"
        return files
    except Exception as e:
        print("cfg err: ", e)


def list_dir(path):
    ldir = os.listdir(path=f'{path}')
    dirs = ''
    for i in range(len(ldir)):
        dirs += f"`{ldir[i]}`\n"
    return dirs
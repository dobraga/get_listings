from os import listdir, remove
from os.path import join

def str_flat(str: str, j:str = "") -> str:
    return j.join(str.split())


def remove_files(dir:str, not_remove:list = []):
    not_remove.append(".gitkeep")

    for file in listdir(dir):
        if not file in not_remove:
            remove(join(dir, file))

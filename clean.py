import os, shutil

from config import pr_path, db_path, sr_path, cpg_path


def clean() -> None:
    if os.path.isdir("workspace"):
        shutil.rmtree("workspace")

    path_list = pr_path, db_path, sr_path
    [shutil.rmtree(f"{path}") for path in path_list if os.path.isdir(f"{path}")]

    if os.path.isfile(f"{cpg_path}"):
        os.remove(f"{cpg_path}")

    if os.path.isfile("time.txt"):
        os.remove("time.txt")

    for path, *X in list(os.walk("."))[::-1]:
        if not os.listdir(path):
            os.rmdir(path)
    [os.makedirs(f"{path}") for path in path_list]

def clean2() -> None:
    """用与一个文件多次调试"""
    path_list = db_path, sr_path    # 只重建data_module/database和slice_module/slice_result
    [shutil.rmtree(f"{path}") for path in path_list if os.path.isdir(f"{path}")]
    [os.makedirs(f"{path}") for path in path_list]


if __name__ == "__main__":
    clean()

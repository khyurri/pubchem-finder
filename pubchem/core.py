import logging
import os
import subprocess
from datetime import datetime

from ftpretty import ftpretty


def info(
    msg_: str,
) -> None:
    now_ = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{now_} [INFO] {msg_}')


def calc_md5(file_path: str) -> str:
    """Uses system utility md5
    todo: if md5 not exists, use python hashlib to calculate hashsum
    :param file_path:
    :return:
    """
    if os.path.exists(file_path):
        output = subprocess.check_output(['md5', file_path]).decode('utf-8')
        return output.split('=')[-1].strip()
    else:
        raise FileNotFoundError(f'File {file_path} is not found')


class FTP:
    def __init__(self, *args, **kwargs):
        self.conn = ftpretty(*args, **kwargs)

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.conn.close()
        except Exception as e:
            logging.error(e)

import os
import sys
import subprocess
import traceback
import requests
import re
import logging
import argparse
from os.path import expanduser

USER_HOME = expanduser("~")
S3_PREFIX_URL = 'https://s3-ap-southeast-1.amazonaws.com/cennznet-snapshots.centralityapp.com/azalea/1.2.2'

DATA_DIR = '/mnt/cennznet'
# DATA_DIR = '/Users/maochuanli/snapshot_mnt_cennznet'
FLAG_FILE = f'{DATA_DIR}/download_snapshot'

def run_cmd(cmd):
    logging.info('CMD: ' + cmd)
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=DATA_DIR)
    result = process.communicate()[0]
    result_txt = result.decode()
    if process.returncode != 0:
        logging.warning('{},{},{}'.format(process.returncode, cmd, result_txt))
    else:
        logging.debug('{},{}'.format(process.returncode, result_txt))
    return process.returncode, result_txt

def download_snapshot_for_node(node_type, snapshot_name=None):
    if os.path.exists(FLAG_FILE):
        if snapshot_name is None:
            index_url = f'{S3_PREFIX_URL}/{node_type}/index.html'
            r = requests.get(index_url, timeout=3)

            snapshot_list = re.findall('href="(\S+)"', r.text)
            for snapshot in snapshot_list:
                logging.warning(snapshot)
            snapshot_name = snapshot_list[-1]
        cmd = f'rm -rf {DATA_DIR}/*'
        rc, out = run_cmd(cmd)

        snapshot_url = f'{S3_PREFIX_URL}/{node_type}/{snapshot_name}'
        logging.info(f'About to download snapshot: {snapshot_url}')
        cmd = f'curl -o x.tar.gz {snapshot_url}'
        rc, out = run_cmd(cmd)
        if rc == 0:
            cmd = 'tar -xzvf x.tar.gz'
            rc, out = run_cmd(cmd)
            logging.info(f'Unzipped snapshot file rc={rc}')
            cmd = 'rm -f x.tar.gz'
            rc, out = run_cmd(cmd)
    else:
        logging.info('No need to download snapshot!')

def main():
    try:
        parser = argparse.ArgumentParser(
            description='Dynamically manage the validator session keys in the current kubernetes cluster')
        parser.add_argument('-t', '--node_type', default='validator', help='node type')
        parser.add_argument('-l', '--log_level', default='INFO', help='logger level')
        args = parser.parse_args()
        log_level = getattr(args, 'log_level')
        node_type = getattr(args, 'node_type')

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            stream=sys.stderr)

        download_snapshot_for_node(node_type)

    except Exception:
        logging.warning(traceback.format_exc())

if __name__ == '__main__':
    main()
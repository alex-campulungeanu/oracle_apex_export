import os
import subprocess
import argparse
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import shutil
import distutils.dir_util

#load env variable / must be on top of the script
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#apex stuff
APP_ID = input(f"What is the APP_ID[{os.getenv('APP_ID')}]: ") or os.getenv('APP_ID')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_SERVICE = os.getenv('DB_SERVICE')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_SID = os.getenv('DB_SID')

#project dir stuff
PRINT_SEPARATOR = '######'
PROJECT_DIR = os.path.abspath(os.getcwd())
APPS_EXPORT_DIR = 'exported_apps'
APEX_SOFTWARE_DIR = 'apex'
APP_EXPORT_DIR = 'f'+str(APP_ID)
APP_EXPORT_PATH = PROJECT_DIR + '\\' + APPS_EXPORT_DIR + '\\' + APP_EXPORT_DIR
APEX_LIB_BASE = PROJECT_DIR + '\\' + APEX_SOFTWARE_DIR

#java stuff
CLASS_PATH=f'.\\ojdbc8.jar;{APEX_LIB_BASE}\\utilities'

#git stuff
COMMIT_MESSAGE=datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def commit_changes():
    print(f'{PRINT_SEPARATOR} Start commiting changes !')
    git_dir=APP_EXPORT_PATH + '\\' + '.git'
    if not os.path.isdir(git_dir):
        print(f'{PRINT_SEPARATOR} Start init project!')
        os.chdir(APP_EXPORT_PATH)
        init_process = subprocess.Popen(['git', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.Popen(['git', 'config', 'core.safecrlf', 'false'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutput_i, stderroutput_i = init_process.communicate()
        os.chdir(PROJECT_DIR) 
        if b'fatal' in stdoutput_i:
            raise Exception('Something went wrong when git init the current project!')
    os.chdir(APP_EXPORT_PATH) 
    subprocess.run(["git", "add", "."], check=True, stdout=subprocess.PIPE).stdout
    commit_process = subprocess.Popen(["git", "commit", "-m", COMMIT_MESSAGE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutput_c, stderroutput_c = commit_process.communicate()
    print(stdoutput_c.decode("utf-8"))
    if stdoutput_c is None:
        print('Nothing to commit !')
    os.chdir(PROJECT_DIR) 


def jar_wrapper(*args):
    os.environ["CLASSPATH"] = CLASS_PATH
    process = subprocess.Popen(['java'] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != '' and line.endswith(b'\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += stdout.split(b'\n')
    if stderr != '':
        ret += stderr.split(b'\n')
    # ret.remove('')
    return ret


def export_app():
    print(f'{PRINT_SEPARATOR} Start Exporting')
    args = ['oracle.apex.APEXExport', 
            '-db', f'{DB_HOST}:{DB_PORT}:{DB_SERVICE}', 
            '-user', DB_USERNAME, 
            '-password', DB_PASSWORD, 
            '-applicationid', APP_ID,
            '-skipExportDate',
            '-split']
    result = jar_wrapper(*args)
    ## if everything ok then move the exported app to exported dir // TODO: create a function for this
    # shutil.move(PROJECT_DIR + '\\' + APP_EXPORT_DIR, APP_EXPORT_PATH, copy_function = shutil.copytree) // this is not working
    distutils.dir_util.copy_tree(PROJECT_DIR + '\\' + APP_EXPORT_DIR, APP_EXPORT_PATH)
    shutil.rmtree(PROJECT_DIR + '\\' + APP_EXPORT_DIR)
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export Oracle APEX application')
    export_app()
    commit_changes()



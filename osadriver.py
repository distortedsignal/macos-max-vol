
import subprocess

class OSAScriptFile(object):

    def __init__(self, filepath: str) -> None:
        self.__original_filepath = filepath
        self.__compiled_filepath = f'{self.__original_filepath}.compiled'
        self.__completed_compile = subprocess.run(['osacompile',
                                                    '-o', self.__compiled_filepath,
                                                    self.__original_filepath])
        self.__completed_compile.check_returncode()

    def run_compiled_file(self):
        return subprocess.run(['osascript', self.__compiled_filepath], capture_output=True)



import subprocess

from typing import List, Optional

class OSAScriptFile(object):

    def __init__(self, filepath: str) -> None:
        self.__original_filepath = filepath
        self.__compiled_filepath = f'{self.__original_filepath}.compiled'
        self.__completed_compile = subprocess.run(['osacompile',
                                                    '-o', self.__compiled_filepath,
                                                    self.__original_filepath])
        self.__completed_compile.check_returncode()

    def run_compiled_file(self, script_args: Optional[List[str]] = None) -> subprocess.CompletedProcess:
        script_call: List[str] = ['osascript', self.__compiled_filepath]

        if script_args:
            script_call.extend(script_args)

        return subprocess.run(script_call, capture_output=True)

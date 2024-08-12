import os
import tempfile
from typing import Union


class Transferable:
    def __init__(self, input_data: Union[os.PathLike, bytes], output_path: os.PathLike):
        self._input = input_data
        self._output_path = output_path

        self._tmp_file: bool = False

    def __enter__(self):
        if isinstance(self._input, bytes):
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            tmp_file.write(self._input)

            self._input = tmp_file.name
            self._tmp_file = True

        return self

    def __exit__(self, *args):
        if self._tmp_file:
            os.remove(self._input)

    @property
    def input_path(self):
        return self._input

    @property
    def output_path(self):
        return self._output_path

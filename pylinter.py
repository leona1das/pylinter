#!/bin/env python
"""
Module for checking pylint on files within a directory
"""
import os
from os import listdir
from os.path import (
    isfile,
    islink,
    join,
)
from subprocess import Popen, PIPE


class PylintLibraryError(Exception):
    """
    Exception raised when errors occurs
    """
    pass


class PylintLibrary:
    """
    Base class for checking directory files and sub-directories
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, cwd, excluded_files, excluded_global):
        self._cwd = cwd
        # Set up absolute paths for excluded files
        self._excluded_files = list(
            map(
                lambda excluded_file: join(cwd, excluded_file),
                excluded_files
            )
        )
        self._excluded_global = excluded_global
        self._valid = True

    @staticmethod
    def __get_pylint_score(output):
        """
        Get score and previous score from pylint standard output
        :param output: Pylint output to be parsed
        :return: Tuple with score and previous result
        """
        strip_string = '\\n\n\'\"'
        score_string = 'Your code has been rated at '
        if score_string not in output:
            return '', ''
        score_part = output.split(score_string)[1].split(' ')
        score = score_part[0].strip()
        if len(score_part) > 1:
            previous = ''
            for value in score_part[1:]:
                previous += value
            # Remove some bad chars that we might fetch
            previous = previous.strip()
        else:
            previous = ''
        return score.strip(strip_string), previous.strip(strip_string)

    def __format_output(self, filename, score, previous):
        """
        Format output
        :param filename: Checked file
        :param score: Score for the current run
        :param previous: Previous score for this file
        """
        message = '{:>8} {:<28} file: {}'.format(score, previous, filename)
        if score == '10.00/10':
            print(message)
        else:
            self._valid = False
            print(message)

    def __check_file(self, absolute_path):
        """
        Check file with pylint
        :param filename: File to be checked
        :param absolute_path: The absolute path for the file
        """
        relative_path = os.path.relpath(absolute_path, self._cwd)
        if not self.__excluded(absolute_path):
            popen = Popen(['pylint', relative_path], stdout=PIPE)
            output, error = popen.communicate()
            if error:
                print(error)
            score, previous = self.__get_pylint_score(str(output))
            self.__format_output(relative_path, score, previous)

    def __excluded(self, filename, directory=False):
        """
        Check if the file is not .py file or should be excluded
        :param filename: File to be checked
        :param directory: True if we are checking a directory
        :return: True if the file/directory should be excluded
        """
        exclude = False
        if islink(filename):
            exclude = True
        elif filename in self._excluded_files:
            exclude = True
        elif not filename.endswith('.py') and not directory:
            exclude = True
        elif directory:
            for exclude_global in self._excluded_global:
                if filename.endswith(exclude_global):
                    exclude = True
        return exclude

    def __check_directory(self, directory):
        """
        Check target directoy
        :param directory: Target directory
        """
        if not self.__excluded(directory, directory=True):
            self.__check_directory_files(directory)

    def __check_directory_files(self, directory):
        """
        Check all files within a directory
        :param directory: Target directory to be checked
        """
        for file in listdir(directory):
            absolute_path = join(directory, file)
            if isfile(absolute_path):
                self.__check_file(absolute_path)
            else:
                self.__check_directory(absolute_path)

    def pylint_directory(self):
        """
        Entry method for checking a directory and all sub-directories
        :raises: PylintLibraryError if not all files has 10.00 score
        """
        self.__check_directory_files(self._cwd)
        if not self._valid:
            raise PylintLibraryError('Some files did not get 10.00 pylint score')


def run(excluded_files, excluded_global, cwd):
    """
    Main method that calls pylint library checker
    :return:
    """
    print("==============")
    print("File Exclusion")
    print("--------------")
    for filename in excluded_files:
        print(filename)
    print("==============")
    pylint_lib = PylintLibrary(cwd, excluded_files, excluded_global)
    pylint_lib.pylint_directory()

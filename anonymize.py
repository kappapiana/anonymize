#!/usr/bin/env python3

# *---------------------------------------------------------------------------
#    SPDX-FileCopyrightText: Carlo Piana <kappa@piana.eu>
#    SPDX-FileCopyrightText: Yaman Qalieh <ybq987@gmail.com>
#
#    SPDX-License-Identifier: AGPL-3.0-or-later
# *---------------------------------------------------------------------------
#
#    ODT and DOCX anonymizer v.0.99
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
# *---------------------------------------------------------------------------
#    This is script is a refactored version of the bash script
#    It should be more consistent and reliable, but mainly it'a an exercise
#    to learn a bit of python.
# *---------------------------------------------------------------------------

import os
import sys
import re
import shutil
import mimetypes
from pathlib import Path
import argparse


# this is just optional in case we want colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class File():
    '''Stores information relevant to each file that is being anonymized.

    Class has following properties:
    name: filename
    file_type: docx or odt
    tmp_dir: location of unzipped file
    '''

    def __init__(self, name, tmp_dir):
        '''Initializes name, tmp_dir, and file_type and
        unzips original file into temporary directory'''
        self.name = name
        self.tmp_dir = cleanup_dir(tmp_dir)

        self.file_type = unzip_file(name, tmp_dir)

        # we establish what kind of string is the original file
        if self.file_type == "odt":
            self.set_odt_strings()
        elif self.file_type == "docx":
            self.set_docx_strings()
        else:
            sys.exit(f"{bcolors.FAIL}{bcolors.BOLD}Error:{bcolors.ENDC} Missing file or file extension: {name}")
            cleanup_dir(args.tmp_dir)

        self.check_textfiles()

    # Document variables set in set_X_strings()
    #
    # regex (dict)
    # Each regex has named groups:
    # pre: constant text before the variable portion
    # body: the data of the tag
    # post: constant text after the variable position
    # Note that the string need to be formatted before use
    #
    # textfiles (list)
    # paths to relevant files within the document archive

    def set_odt_strings(self):
        self.regex = {
            "author": "(?P<pre><dc:creator>)(?P<body>{})(?P<post><\/dc:creator>)",
            "initials": "(?P<pre><meta:creator-initials>)(?P<body>{})(?P<post><\/meta:creator-initials>)",
            "dates": "(?P<pre><dc:date>)(?P<body>{})(?P<post><\/dc:date>)",
        }
        self.textfiles = [os.path.join(self.tmp_dir, "content.xml")]

    def set_docx_strings(self):
        self.regex = {
            "author": "(?P<pre>w:author=\")(?P<body>{})(?P<post>\")",
            "initials": "(?P<pre>w:initials=\")(?P<body>{})(?P<post>\")",
            "dates": "(?P<pre>w:date=\")(?P<body>{})(?P<post>\")",
        }
        self.textfiles = [os.path.join(self.tmp_dir, 'word', xml)
                          for xml in ["comments.xml", "document.xml", "footnotes.xml"]]

    def check_textfiles(self):
        final = []
        for textfile in self.textfiles:
            if os.path.isfile(textfile):
                final.append(textfile)
            else:
                print(f"{bcolors.WARNING}{bcolors.BOLD}Warning:{bcolors.ENDC} Skipping expected file: {textfile}")
        self.textfiles = final

    def replace(self, from_string, to_string, regex, regex_function=False):
        ''' Replace text in self.textfiles based on specified regex.

        from_string: string or regex string to insert into main tag
        to_string: string or lambda to replace from_string with after matching
        regex: self.regex key to format with from_string. If None, replace from_string
        '''
        if regex is None:
            regex = re.compile(from_string)
        else:
            regex = re.compile(self.regex[regex].format(from_string))
            # to_string can also be a lambda function, which should implement this itself
            if type(to_string) == str:
                to_string = f"\\g<pre>{to_string}\\g<post>"



        for textfile in self.textfiles:
            with open(textfile, 'r') as f:
                file_contents = regex.sub(to_string, f.read())
            with open(textfile, 'w') as f:
                f.write(file_contents)

    def find_authors(self):
        content = []
        for textfile in self.textfiles:
            with open(textfile, 'r') as f:
                content = content + re.findall(self.regex["author"].format(".*?"), f.read())
        # Only the second element in the list of tuples is the authors
        return set([x[1] for x in content])


    def delete_initials(self):
        '''replaces the content of the initials tag with an empty string. It doesn't
        ask for permission though, returns nothing'''
        self.replace(".*?", "", "initials")

    def delete_dates(self):
        '''replaces the content of the date tag with an empty string. It doesn't
        ask for permission though, returns nothing'''
        # Replace with the datetime for 0
        # See https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#dateTime
        self.replace(".*?", "0001-01-01T00:00:00", "dates")

    def rezip(self, output_prefix, output_dir):
        # Recreate a version of the file with the new content in

        output_file = os.path.join(output_dir, output_prefix + self.name)
        shutil.make_archive(output_file, "zip", self.tmp_dir)

        output_file_zip = output_file + ".zip"

        # Rename it to the original extension
        os.rename(output_file_zip, output_file)

        # function returns the name of the changed file
        return output_file


def cleanup_dir(dir="/tmp/anonymize/"):
    ''' cleans the working directory '''

    if os.path.isdir(dir) is True:

        for files in os.listdir(dir):
            path = os.path.join(dir, files)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)
    else:
        try:
            os.mkdir(dir)
        except OSError:
            print("\nCreation of the directory %s failed" % dir)

            # Creates dir with trailing slash even if not in input
            # oftentimes people don't add
            dir = os.path.join(input("insert alternative temporary directory \n:> "), '')

            if os.path.isdir(dir) is True:  # if dir exists already, use it
                pass
            elif os.path.isfile(dir) is True:  # it's a file, cant use this
                print(f"sorry {dir} is an existing file can't create dir")
                print("make sure to find another directory where you "
                      "have permissions")
                sys.exit('...quitting.')
            else:
                os.mkdir(dir)
        else:
            print("\nSuccessfully created the directory %s " % dir)

    return dir


def unzip_file(orig_file, tmp_dir):
    '''odt and docx are zip. We send them to a convenient location and work on
    that extracted stuff. Also, we check if the file type is correct, else, we
    abort, since we don't know how to handle different files'''

    type = mimetypes.guess_type(orig_file)
    if type[0] == "application/vnd.oasis.opendocument.text":
        filetype = "odt"
    elif type[0] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        filetype = "docx"
    else:
        return

    shutil.unpack_archive(orig_file, tmp_dir, 'zip')
    return filetype


def cycle_ask(cur_files):
    '''opens and reads file to be changed, asks for input until user is fine
    then writes the changed string, until you call it quits. This is sort of the
    main function here'''

    # Flatten list of lists structure
    filelist = [item for subfile in cur_files for item in subfile.textfiles]

    while True:

        # here we find the authors
        authors_list = find_all_authors(cur_files)

        # Add more commands to the list of possible authors
        additional_commands = {
            "a": "all",
            "n": "number all",
            "q": "quit"
        }

        # FIXME: we read the values, but we still can't work out writing the file

        commands = {**authors_list, **additional_commands}

        # Present the selection menu
        print(f"\nSelect values that you want to change from this "
              f"list, or {bcolors.OKCYAN}a{bcolors.ENDC} for all, \nor {bcolors.OKCYAN}q{bcolors.ENDC} to quit:\n")
        for key in commands:
            print(f"{key}: {commands.get(key)}")

        # gets the value from input key
        from_string = commands.get(input(f"\n{bcolors.BOLD}\n:> {bcolors.ENDC} "))

        if from_string is None:
            print(f"{bcolors.WARNING} \nyou have selected {from_string} but admissible values are the ones presented to you {bcolors.ENDC}")
            print(f"You {bcolors.BOLD}definitely{bcolors.ENDC} should use one of those keys: \n")

        # If you select quit, we are over
        elif from_string == "quit":
            break

        elif from_string == "all":
            print("\nYou have selected to change all values"
                  "\nPlease enter the string you want to change"
                  f" {bcolors.BOLD}to{bcolors.ENDC} \n")

            from_string = "|".join([re.escape(a) for a in authors_list.values()])
            to_string = input(":> ")

            for cur_file in cur_files:
                cur_file.replace(from_string, to_string, "author")

        elif from_string == "number all":
            print("\nYou have selected to number all authors"
                  "\nPlease enter the string to prepend to each number"
                  "\nEx: 'Reviewer' => 'Reviewer' 1, 'Reviewer' 2, ... \n")

            prefix = input(":> ")

            from_string = "|".join(authors_list.values())

            # Create a repl function to pass to re.sub
            reversed_authors = {author: num for num, author in authors_list.items()}
            to_string = lambda x: f"{x.group('pre')}{prefix} {reversed_authors.get(x.group('body'), x.group('body'))}{x.group('post')}"

            for cur_file in cur_files:
                cur_file.replace(from_string, to_string, "author")
                # for n, author in authors_list.items():
                #     cur_file.replace(re.escape(author), f"{prefix} {n}")

        # othewise, you have selected a good key, let's replace it with
        # something and start over
        else:
            print(f"You have selected {from_string}")
            to_string = input(f"\nPlease enter the string you want to change {bcolors.BOLD}to{bcolors.ENDC} \n\n:> ")

            for cur_file in cur_files:
                cur_file.replace(re.escape(from_string), to_string, "author")


def rezip(cur_files, output_prefix, output_dir):
    '''rewraps everything'''
    return [f.rezip(output_prefix, output_dir) for f in cur_files]


def find_all_authors(cur_files):
    '''finds and lists authors in content xml file returning a dictionary of
    values: this is necessary to know what authors we have since last change '''

    authors = [f.find_authors() for f in cur_files]
    authors_list = sorted(set().union(*authors),
                          key = lambda s: s.lower())  # sort in lowercase

    # assign number to each option, starting from 1
    authors_dict = {str(i+1): author
                    for i, author in enumerate(authors_list)}
    def rezip(self, output_prefix, output_dir):
        # Recreate a version of the file with the new content in it

        output_file = os.path.join(output_dir, output_prefix + self.name)
        output_file = os.path.join(output_dir, output_prefix + os.path.basename(self.name))
        shutil.make_archive(output_file, "zip", self.tmp_dir)

        output_file_zip = output_file + ".zip"
    return authors_dict

def delete_initials(cur_files):
    '''replaces the content of the initials tag with an empty string. It doesn't
    ask for permission though, returns nothing'''

    for cur_file in cur_files:
        cur_file.delete_initials()

    print("\n++++++++++++++++++++++++++++++++++++")
    print(f"\n{bcolors.OKCYAN}    we have deleted the initials{bcolors.ENDC}\n")
    print("++++++++++++++++++++++++++++++++++++\n")

def delete_dates(cur_files):
    '''Deletes the dates associated with comments, returns nothing'''

    for cur_file in cur_files:
        cur_file.delete_dates()

    print("\n++++++++++++++++++++++++++++++++++++")
    print(f"\n{bcolors.OKCYAN}    we have deleted the dates{bcolors.ENDC}\n")
    print("++++++++++++++++++++++++++++++++++++\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Anonymize documents.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("filenames", metavar="FILE", type=str, nargs="+",
                        help="Path to the files to anonymize")
    parser.add_argument("--tmp-dir", type=str, default="/tmp/anonymize",
                        help="Temporary directory to work with")
    parser.add_argument("--output-prefix", type=str, default = "_anon_",
                        help="Prefix for output files.")
    parser.add_argument("--output-dir", type=str, default = Path.cwd(),
                        help="Directory for output files")
    parser.add_argument("--keep-dates", action="store_true",
                        help="Keep the comment dates")
    parser.add_argument("--keep-initials", action="store_true",
                        help="Keep the commenter initials")
    args = parser.parse_args()

    # Cleanup the main tmp_dir
    cleanup_dir(args.tmp_dir)

    # Make a tmp directory for each file and unzip the file there
    # Creates a list of File
    files = [File(filename, os.path.join(args.tmp_dir, str(i)))
             for i, filename in enumerate(args.filenames)]

    cycle_ask(files)

    if not args.keep_initials:
        delete_initials(files)

    if not args.keep_dates:
        delete_dates(files)

    anonymized_files = rezip(files, args.output_prefix, args.output_dir)
    for anonymized in anonymized_files:
        print(f"{bcolors.OKGREEN}file is now in {anonymized}{bcolors.ENDC}\n")


    cleanup_dir()

    # TODO:

    # Add create dir

#!/usr/bin/env python3

# *---------------------------------------------------------------------------
#    SPDX-FileCopyrightText: Carlo Piana <kappa@piana.eu>
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

cwd = Path.cwd()  # Current directory is cwd


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


# Get the first argument as the modified file
zipped_file_name = sys.argv[1]

# Set the relevant part to be changed in file source
odt_string = "<dc:creator>(.*?)</dc:creator>"
doc_string = "w:author=\"(.*?)\""


def cleanup_dir(dir="/tmp/test/"):
    ''' cleans the working directory, using the global variable
    no need to pass arguments '''

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


def unzip_file(orig_file):
    '''odt and docx are zip. We send them to a convenient location and work on
    that extracted stuff. Also, we check if the file type is correct, else, we
    abort, since we don't know how to handle different files'''

    type = mimetypes.guess_type(orig_file)
    if type[0] == "application/vnd.oasis.opendocument.text":
        print("It's a boy!")
        filetype = "odt"
    elif type[0] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        filetype = "docx"
    else:
        print("It's a monkey!")

    shutil.unpack_archive(zipped_file_name, export_dir, 'zip')
    return filetype


def replace_text(target_string, from_string, to_string):
    ''' gets input string to replace ad substitutes it with the corresponding
    string in target file, very simple and straightforward'''

    search_replace = re.sub(from_string, to_string, target_string)

    return search_replace

def create_megastring(unzipped_files):

    '''accepts an array of files and appends the content, so we search
    everything'''

    target_string = "" # create the variable as an empty string
    counter = 0


    for file in unzipped_files:

        if os.path.exists(file):

            f = open(file, 'r')
            target_string_temp = f.read()
            target_string = f'{target_string} {target_string_temp}'
            changed_text = ""  # this will avoid errors when quitting without changing
            print("\nWe read", file)
            counter +=1
            print(counter)
            f.close()

        else :
            print("\nThe search file is missing:", file)

    return(target_string)


def cycle_ask(cur_filename):
    '''opens and reads file to be changed, asks for input until user is fine
    then writes the changed string, until you call it quits. This is sort of
    the main function here'''


    while True:

         # here we find

        authors_list = find_authors(create_megastring(cur_filename))

        # Add more commands to the list of possible authors
        additional_commands = {
            "a": "all",
            "q": "quit"
        }

        # FIXME: we read the values, but we still can't work out writing the file

        commands = {**authors_list, **additional_commands}

        # Present the selection menu
        print("\nSelect values that you want to change from this"
              "list, or a fro all, or q to quit:\n")
        for key in commands:
            print(f"{key}: {commands.get(key)}")

        # gets the value from input key
        from_string = commands.get(input(f"\n{bcolors.BOLD}\n:> {bcolors.ENDC} "))

        if from_string is None:
            print(f"{bcolors.WARNING} \nyou have selected {from_string} but admissible values are the ones presented to you {bcolors.ENDC}")
            print(f"You {bcolors.BOLD}definitely{bcolors.ENDC} should use one of those keys: \n")

        # If you select quit, we are over
        elif from_string == "quit":
            # We have finished changing the target string, write it into file.
            print("ok, we stop here")
            # f.close()
            try:
                test = target_string_local
                len(test)

            #     f = open(cur_filename, 'w')
            #     f.write(changed_text)
            #     f.close()
            except Exception as e:
                str(e)
                print(e)
                print(f"\n{bcolors.BOLD}*** we have not changed anything{bcolors.ENDC} *** \n")

            break

        elif from_string == "all":
            print("\nYou have selected to change all values"
                  "\nPlease enter the string you want to change"
                  f" {bcolors.BOLD}to{bcolors.ENDC} \n")

            to_string = input(":> ")

            for file in cur_filename:

                k = open(file, 'r')
                target_string_local = k.read()

                for key in authors_list:
                    from_string = authors_list.get(key)
                    changed_text = replace_text(target_string_local, from_string, to_string)
                    target_string_local = changed_text

                k.close()
                k = open(file, 'w')
                k.write(changed_text)
                k.close()

        # othewise, you have selected a good key, let's replace it with
        # something and start over
        else:
            print(f"You have selected {from_string}")
            to_string = input(f"\nPlease enter the string you want to change {bcolors.BOLD}to{bcolors.ENDC} \n\n:> ")

            for file in cur_filename:

                k = open(file, 'r')
                target_string_local = k.read()

                changed_text = replace_text(target_string_local, from_string, to_string)
                target_string_local = changed_text

                k.close()
                k = open(file, 'w')
                k.write(changed_text)
                k.close()


def rezip():
    '''rewraps everyting'''

    anon_textfile = os.path.join(cwd, '_anon_') + zipped_file_name

    # Recreate a version of the file with the new content in it
    shutil.make_archive(anon_textfile, "zip", export_dir)

    anon_textfile_zip = anon_textfile + ".zip"

    # Rename it to the original extension FIXME: this is a hack
    os.rename(anon_textfile_zip, anon_textfile)

    # function returns the name of the changed file
    return anon_textfile


def find_authors(in_text):
    '''finds and lists authors in content xml file returning a dictionary
    of values '''

    authors = set(re.findall(author_string, in_text))
    author_list = sorted(authors, key= lambda s: s.lower())  # sort in lowercase
    authors_dict = {}
    counter = 1
    for i in author_list:
        index = str(counter)
        authors_dict[index] = i
        counter += 1

    return authors_dict


# Let's run it

export_dir = cleanup_dir()

file_type = unzip_file(zipped_file_name)

# we establish what kind of string is the original file

if file_type == "odt":
    author_string = odt_string
    textfile0 = export_dir + "content.xml"
    textfile = [textfile0] #just to use a multifile structure, don't change
elif file_type == "docx":
    author_string = doc_string
    textfile0 = os.path.join(export_dir, 'word', '') + "document.xml"
    textfile1 = os.path.join(export_dir, 'word', '') + "comments.xml"
    textfile = [textfile0, textfile1]

else:
    print("It's a monkey!")
    sys.exit('not do')
    cleanup_dir()

cycle_ask(textfile)

anonymized = rezip()

print(f"file is now in {anonymized}")

cleanup_dir()

# TODO:

# Add create dir

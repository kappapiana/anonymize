import os, sys, re, shutil, mimetypes

zipped_file_name = sys.argv[1]

cwd = os.getcwd()
export_dir = "/tmp/test"
textfile = export_dir + "/content.xml"

def unzip_file(orig_file) :
  print(orig_file)
  type = mimetypes.guess_type(orig_file)

  if type[0] == "application/vnd.oasis.opendocument.text" :
    print("It's a boy!")
    filetype = "odt"
  elif type[0] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" :
    print("It's a girl docx")
    filetype = "docx"
  else :
    print("It's a monkey!")

  shutil.unpack_archive(zipped_file_name, export_dir, 'zip')

  return filetype

def replace_text(target_string, from_string, to_string) :
  ''' gets input string to replace ad substitutes it with the corresponding string in target file'''

  search_replace = re.sub(from_string, to_string, target_string)

  return search_replace


def cycle_ask(cur_filename) :
    '''opens and reads file to be changed, asks for input until user is fine
    then writes the changed string.'''

    f = open(cur_filename, 'r')
    target_string = f.read()

    print(find_authors(target_string))

    while  True :

        from_string = input("\nPlease enter the string you want to change **from**\n\n :> ")

        for_string = input("\nPlease enter the string you want to change **to** \n\n :> ")

        changed_text = replace_text(target_string, from_string, for_string)

        if input('Do You Want To Continue? [enter "stop" to stop | leave empty to continue]') == 'stop' :
        # We have finished changing the target string, write it into the file.
          print("ok, we stop here")
          f.close()
          f = open(cur_filename, 'w')
          f.write(changed_text)
          f.close()
          break

        else :

        # the target string must be the modified string this time:
          print("another time -- authors are: \n")
          print(find_authors(changed_text))
          target_string = changed_text


def rezip() :

  anon_textfile = cwd + "/_anon_" + zipped_file_name

  # Recreate a version of the file with the new content in it
  shutil.make_archive(anon_textfile, "zip", export_dir)

  anon_textfile_zip = anon_textfile + ".zip"

  # Rename it to the original extension FIXME: this is a hack
  os.rename(anon_textfile_zip, anon_textfile)

  # function returns the name of the changed file
  return anon_textfile

def find_authors(in_text) :
    '''finds authors in odt conten xml file '''
    # TODO: the string can be made universal

    authors = set(re.findall("<dc:creator>(.*?)</dc:creator>", in_text))
    authors_dict = {}
    counter = 1
    for i in authors :
        index = f"author {counter}"
        authors_dict[index] =  i
        counter += 1

    return authors_dict


# Let's run it

type = unzip_file(zipped_file_name)

if type[0] == "odt" or  "doc" :
    print("let'z continue!")

else :
    print("It's a monkey!")
    sys.exit('not do')


cycle_ask(textfile)

anonymized = rezip()

print(f"file is now in {anonymized}")


# TODO:
# - make target file and regexp for docx
# - automagically recognize fileformat and decide which function
# - make function class and subclasses for odt and docx

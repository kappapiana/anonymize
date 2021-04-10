import os, sys, re, shutil

zipped_file_name = sys.argv[1]

cwd = os.getcwd()
export_dir = "/tmp/test"
textfile = export_dir + "/content.xml"

def unzip_file(orig_file) :
  print(orig_file)
  shutil.unpack_archive(zipped_file_name, export_dir, 'zip')


def replace_text(filename) :
  ''' opens the file ad substitutes
  the corresponding string'''

  f = open(filename, 'r')

  # regexp = "r" + "\"" + regexp + "\""

  # setting flag and index to 0
  flag = 0
  index = 0

  readfile = f.read()

  from_string = ""
  f.close()

  while from_string != "quit" :

      from_string = input("\nPlease enter the string you want to change **from**\nIf you want to end, enter \"quit\" \n :> ")

      if from_string != "quit" :
          f = open(filename, 'w')
          for_string = input("\nPlease enter the string you want to change **to** \n\n :> ")

          search_replace = re.sub(from_string, for_string, readfile)

          f.write(search_replace)

  f.close()

def rezip() :

  anon_textfile = cwd + "/_anon_" + zipped_file_name

  # Recreate a version of the file with the new content in it
  shutil.make_archive(anon_textfile, "zip", export_dir)

  anon_textfile_zip = anon_textfile + ".zip"

  # Rename it to the original extension FIXME: this is a hack
  os.rename(anon_textfile_zip, anon_textfile)

  # function returns the name of the changed file
  return anon_textfile

def find_authors(filename) :
    f = open(filename, 'r')
    readfile = f.read()
    authors = set(re.findall("<dc:creator>(.*?)</dc:creator>", readfile))
    authors_dict = {}
    counter = 1
    for i in authors :
        index = f"author {counter}"
        authors_dict[index] =  i
        counter += 1

    f.close()

    return authors_dict


# Let's run it

unzip_file(zipped_file_name)

authors_list = find_authors(textfile)

print(f"authors are {authors_list}")

replace_text(textfile)

anonymized = rezip()

print(f"file is now in {anonymized}")


# TODO:
# - make target file and regexp for docx
# - automagically recognize fileformat and decide which function
# - make function class and subclasses for odt and docx

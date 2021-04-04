import zipfile, os, sys, re


zipped_file_name = sys.argv[1]

cwd = os.getcwd()
export_dir = "/tmp/test"
textfile = export_dir + "/content.xml"

def unzip_file(orig_file) :
  with zipfile.ZipFile(orig_file, 'w') as zip_ref:
    zip_ref.extractall(export_dir)



def replace_text(filename, regexp, replace) :
  ''' opens the file ad substitutes
  the corresponding string'''

  f = open(filename, 'r')

  # regexp = "r" + "\"" + regexp + "\""

  print("replace " + regexp)
  print(f"with: {replace}")


  # setting flag and index to 0
  flag = 0
  index = 0

  readfile = f.read()
  search_replace = re.sub(regexp, replace, readfile)

  f.close()

  f = open(filename, 'w')

  f.write(search_replace)

  f.close()

  print(f"I have changed {regexp} with {replace} in {filename}")

unzip_file(zipped_file_name)

replace_text(textfile, "Avv. Carlo Piana", "fuffa")


print("Bye")

#!/usr/bin/env bash

# *---------------------------------------------------------------------------
#    ODT and DOCX anonymizer v.0.99
#    Copyright (C) 2020 Carlo Piana
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

red=$(tput setaf 1)
green=$(tput setaf 76)
normal=$(tput sgr0)
bold=$(tput bold)
underline=$(tput sgr 0 1)

# instout="install_output.log"
# insterr="install_error.log"
declare -a authors_array=()
declare -a authors_array_plus=()
author_string=""
orig_filename="$1"

i_ok() { printf "${green}✔${normal}\n"; }
i_ko() { printf "${red}✖${normal}\n...exiting, check logs"; }


# some variables that will be used and make sure the zip dir exists

curdir=`pwd`
filename="_anonymized_$1"
zipdir="/tmp/libreoffice"

mkdir $zipdir 2&> /dev/null
rm -rf ${zipdir:?}/*

function check_i {
  if [ $? -eq 0 ]; then
    i_ok
  else
    i_ko; read -r
    exit
  fi
}

function substitute_it {

  if  [[ $(file --mime-type -b "$orig_filename") =~ application/vnd.oasis.opendocument.text ]] ; then

  sed -i -E s@"(or>)$name_from(<)"@"\1$name_to\2"@g $zipdir/*.xml

elif [[ $(file --mime-type -b "$orig_filename") =~ application/vnd.openxmlformats-officedocument.wordprocessingml.document ]]; then

  content_dir=`find $zipdir -mindepth 2 -name '*.xml' | cut -f 1,2,3,4 -d /`

  for d in $content_dir ; do

  sed -i -E s@"(author=\")$name_from(\")"@"\1$name_to\2"@g $d/*.xml
  sed -i -E s@"(By>)$name_from(<)"@"\1$name_to\2"@g $d/*.xml ; done # caputure some metatags as well

else
  echo "WTF"
fi
}

function list_authors {

mapfile -t authors_array < <(grep -hoP "$author_string" $zipdir -R | sort | uniq | sed -E "s@$author_string@\1@g")

			echo "+----------------------------------------------------------------"
if [[ ${#authors_array[*]} == 1 ]] ; then
  printf "The author is: "
  printf "%s " "${authors_array[@]}."
else
  printf "Authors are: "
  printf "\"%s\" " "${authors_array[@]}"
fi
      printf "\n"
			echo "+----------------------------------------------------------------"
}

function change_all {

	printf "Please insert the name you want to be ${red}the only one${normal} displayed in revisions \n"

	printf "instead of all the above\\n\\n${green}: > ${normal}"

	read -r name_to

	printf "\\nThanks, we are going to replace everything with ${green}$name_to${normal} \\n"

	for i in "${authors_array[@]}" ; do

    name_from="$i"

    substitute_it

	done

}


function choose_subs { # FIXME: make the choice only from the authors_array array
authors_array_plus=("${authors_array[@]}" "list" "quit")
quit_no=("${#authors_array_plus[*]}")
list_no=$(( quit_no - 1 ))

printf "${underline}You have the following choices:${normal}\\n"
PS3=""$'\n'"Choose 1 to ${#authors_array[*]} to modify actual values;"$'\n'"${list_no} to list, ${quit_no} to exit;"$'\n'"Make your choice: ${green}:>${normal} "

select value in "${authors_array_plus[@]}"
do
if [[  ${value} == "quit" ]] ; then
  printf "\\nThanks! and goodbye\\n\\n"
  break
elif [[ ${value} == "list" ]] ; then
  list_authors
  choose_subs # restart from beginning to recreate menu. Cases change.
  exit 0 # otherwise it returns to the function
else

    name_from="${value}"


printf "insert the name you want to ${bold}change ${value} into${normal}\\n:> "
    read -r name_to

substitute_it

fi
done

}

clear

# Checking the required number of variables

[ ! -z $1 ] && printf "\nFilename is present "|| (printf "missing variable, sucker, a namefile is expected " && exit 1)
check_i

#checking if correct filetype

if
[[ $(file --mime-type -b "$1") =~ application/vnd.oasis.opendocument.text ]] ; then

printf "\\nGood file type ODT"

author_string="<dc:creator>(.*?)</dc:creator>"

elif

[[ $(file --mime-type -b "$1") =~ application/vnd.openxmlformats-officedocument.wordprocessingml.document ]]; then

printf "\\nGood filetype OOXML "

author_string="w:author=\"(.*?)\""

else
	 (printf "\\nNot an ODT nor an OOXML document, can't do " && exit 1)
fi
check_i

printf "\nThis is the list of current authors,
now you will be asked to chose what you want to make of them: \n"

 unzip -oq "$1" -d $zipdir
 check_i

 list_authors

# ok, we're ready, let's meddle with the content!


# Mock select menu

printf "Please enter your choice: \\n\\n"
options=("Change all" "Change only one")
select opt in "${options[@]}"
do
	case $opt in
		"Change all")
		break
		;;
		"Change only one")
		break
		;;
		*) echo "invalid option $REPLY";;
	esac
done

printf "\\n"

	# Now we ask for input


  if [ "$REPLY" = "1" ]; then

 	change_all

	printf "\\nnow the list of authors is: \\n"

	list_authors

  else

  choose_subs

  printf "\\nnow the list of authors is: \\n"

  list_authors

  fi

		# this is a dirty hack, because I could not add to zipfile from outside the directory
		# basing the directory with -b did not work hell knows why
		# I am SO LAME

		# cp $1 $filename # needed to have correct structure FIXME

		cd "$zipdir" || exit 1# in case cd fails
    check_i
    printf " move to zip directory; \\n\\n"

		# touch "$curdir/$filename"
    rm "$curdir/$filename"


    find -print | zip "$curdir/$filename" -@ 1>/dev/null

		cd "$curdir" || exit 1 # in case it fails
    check_i
    printf " recreated file from zip directory; \\n\\n"

echo "

${green}Script complete${normal}

***${bold}WARNING${normal}***  Newfile is in $curdir/${bold}$filename${normal}

We are not going to replace the original file, we play it safe.

"

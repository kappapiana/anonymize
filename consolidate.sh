#!/usr/bin/env bash

filename=$1

searchstring=$"(\<text:changed-region xml:id=\")(.*?)(\".*?<dc:creator>)(.*?)(\<\/dc:creator\>.*?author=\")(.*?)(\".*?\</text:changed-region\>)"

sed -E -i s@"(/text:changed-region>)"@"\1\\n"@g $filename
#
# # echo "|$searchstring|"
#
# string_match=$(grep -P -m1 -o "${searchstring}" ${1})

two_auths=$(grep -P -m1 -o "${searchstring}" ${1}  | perl -p -e s@"${searchstring}"@"\4+\6+\2"@)

printf "\n ecco ${two_auths}"

auth1=$(printf "${two_auths}" |awk  'BEGIN { FS = "+" } ; {print $1}')

auth2=$(printf "${two_auths}" |awk  'BEGIN { FS = "+" } ; {print $2}')

xml_id=$(printf "${two_auths}" |awk  'BEGIN { FS = "+" } ; {print $3}')

printf "\nIl primo nome è ${auth1} \n"
printf "Il secondo nome è ${auth2} \n\n"
printf "Il terzo nome è ${xml_id} \n\n"

searchstring_inside=$"(\<text:changed-region xml:id=\")(${xml_id})(\".*?<dc:creator>)(.*?)(\<\/dc:creator\>.*?author=\")(.*?)(\".*?\</text:changed-region\>)"
searchstring_inside_place=$"(\<text:change text:change-id=\"$xml_id\"/\>)"

printf "la stringa da modificare è ${searchstring_inside}"

if [[ $auth1 == $auth2 ]]; then

   perl -p -i.bak -e s@"${searchstring_inside}"@@g $filename
   perl -p -i.bak -e s@"${searchstring_inside_place}"@@g $filename


else
  echo "no figata"
fi

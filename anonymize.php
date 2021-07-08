<?php

$zipFile = 'Document.docx'; // PASS TO FUNCTION
$name_to_add = null; // PASS TO FUNCTION. If you want to put a name for everything, this is where you specify it

if (file_exists($zipFile) === false) { // Validate file
    throw new \Exception('Cannot find archive file.');
}

$zip = new \ZipArchive();
if (!$zip->open($path) || $zip->numFiles == 0){ // Either empty (Made new ZipArchive of file???) or not a zip file
    return false;
}

/**
 * To add new item, basic regex is
 * `"/({XML Attribute}{Starting Char/Chars}).*?({Ending Char/Chars})/"`
 * 
 * `.*?` selects everything between the previous and next regex statements.
 * By placing the previous and next regex statements in parentheses, the 
 * replace statement can be generalized to $1$2, meaning, part 1 + part 2
 */
$regex = [
    "/(author=\").*?(\")/",
    "/(initials=\").*?(\")/",
    "/(name=\").*?(\")/",
    "/(userId=\").*?(\")/",
    "/(By>).*?(<)/",
    "/(creator>).*?(<)/",
    "/(lastModifiedBy>).*?(<)/",
];

$tempNames = [];
for( $i = 0; $i < $zip->numFiles; $i++ ){ 
    if ((pathinfo($zip->getNameIndex($i), PATHINFO_EXTENSION) == 'xml') && (preg_match("/document\.xml|slide[0-9]*\.xml/", $zip->getNameIndex($i)) == false)){
        // Get anonymized file

        $content = preg_replace($regex, "$1".$name_to_add."$2", $zip->getFromIndex($i));

        // Write to file
        array_push($tempNames, stream_get_meta_data(tmpfile())['uri']);
        $tmp = fopen(end($tempNames), 'w+');

        /**
         * This ensures fwrite can actually write the whole file.
         * Block size assumed to be 4096, as standard in Win and Linux.
         */
        $pieces = str_split($content, 1024 * 4); 
        foreach ($pieces as $piece) {
            fwrite($tmp, $piece);
        }
        fclose($tmp);

        // Save in zipArchive
        $zip->addFile(end($tempNames), $zip->getNameIndex($i));
    }
}
$zip->close();
foreach ($tempNames as $tmpName) {
    unlink($tmpName);
}
return true;

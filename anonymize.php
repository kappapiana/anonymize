<?php

$zipFile = 'Document.docx'; // PASS TO FUNCTION

if (file_exists($zipFile) === false) { // Validate file
    throw new \Exception('Cannot find archive file.');
}

$zip = new \ZipArchive();
if ($zip->open($zipFile)) {
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

for( $i = 0; $i < $zip->numFiles; $i++ ){ 
    if (pathinfo($zip->getNameIndex($i), PATHINFO_EXTENSION) == 'xml'){
        // Get anonymized file
        $content = preg_replace($regex, "$1$2", $zip->getFromIndex($i));

        // Write to file
        $name = stream_get_meta_data(tmpfile())['uri'];
        $tmp = fopen($name, 'w+');
        $pieces = str_split($content, 1024 * 4); // This ensures fwrite can actually write the whole file. Block size assumed to be 4096, as standard in Win and Linux
        foreach ($pieces as $piece) {
            fwrite($tmp, $piece);
        }
        fclose($tmp);

        // Save in zipArchive
        $zip->addFile($name, $zip->getNameIndex($i));
    }
}
$zip->close();
return true;

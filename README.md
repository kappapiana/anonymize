<!--
 *---------------------------------------------------------------------------
    SPDX-FileCopyrightText: Carlo Piana <kappa@piana.eu>

    SPDX-License-Identifier: CC0-1.0
 *---------------------------------------------------------------------------
 -->

[![REUSE status](https://api.reuse.software/badge/github.com/kappapiana/anonymize)](https://api.reuse.software/info/github.com/kappapiana/anonymize)

# ODF and DOCX anonymizer

This script `anonymize.py` does one thing and hopefully it does it well. It allows changing the metadata to comment and track changes and hopefully also other metadata to a document.

For those better used to `bash` script or not fancy with installing python, `anonymize.sh` is an old and not actively developed (probably broken) verision.

## Rationale

The idea came from working as an editor of a peer-reviewed journal (see https://jolts.world).

Reviews are half-blind and are done in ODT via Libreoffice, as a preference. However,
the best way to provide feeback -- redlines and comment -- give away the author's name, thus the reviewer's. It is possible to change the settings in Libreoffice, but out of experience very few care (even if properly instructed). Or they realize it halfway through.

Therefore I needed something to sanitize the data.

## Second thought

As a lawyer, I frequently do the same with clients. I change something, clients change something, but we don't want to make it transparent to the other party when we exchange the document. So I want to consolidate my edits and clients'.

If you put the two under the same name, they get automagically consolidated. So you have one single contributor for your edits, and anybody else remains visible.

This is the second option.

## Third thought, docx

But I also needed that the many time (most of the time) when I have to clean up the mess of multiple internal edits with clients working in docx. Therefore I have added the same structure (also OOXML is an XML bunch of files zipped together) for that file, without the need to convert them in ODT as I used to do before.

So it will also work with docx (OOXML text document), although MS Word® has a feature to change data as an afterthought (but all or none, AFAICR) and this script might not be strictly necessary.

## Fourth thought, python3

I have attempted a porting to python3, actually everything has been rewritten with some more sense. It should work for any operating system, as I have abstracted the paths via the `os` library. Hopefully.

# HOWTO BASH

Requires a recently updated version of Linux (I target bash 4.0, roughly), preferably git (but it's not necessary) and a working knowledge of running scripts. The easiest way is to clone the repository somewhere and point to the script from the command line.

This is still work in progress, but it's now reasonably good to go.

Suppose that you have installed (copied) it in `~/scripts/anonymize.sh` and that your documenti is in `~/documents/doc.odt`

Do this:

```shell
ls -l ~/scripts/anonymize.sh # (make sure it's "executable")
```

if it is not executable

```shell
sudo chown a+x ~/scripts/anonymize.sh
```

Now you can run the script

```shell
cd ~/documents/
~/scripts/anonymize.sh doc.odt
```
It will interact with you asking if you want to change everything in one go or one author by one. Eventually you will (hopefully) have a file named like `_anonymized_doc.odt`. I'm not copying it over so that you can review the result without risking to destroy everything...


# HOWTO python

It should be sufficient to have a running python3 environment, the imported libraries are all from the standard set.

just run

```
[script_directory]/anonymize.py filename.[odt|docx]

```

from any directory and it should produce a copy with `_anon_` prepended to the filename


## TODO


- [ ] remove also document creator, for full anonymization (now only creators)
- [ ] make it work also for documents without comments!

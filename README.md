<!--
 *---------------------------------------------------------------------------
    SPDX-FileCopyrightText: Carlo Piana <kappa@piana.eu>

    SPDX-License-Identifier: CC0-1.0
 *---------------------------------------------------------------------------
 -->

[![REUSE status](https://api.reuse.software/badge/github.com/kappapiana/anonymize)](https://api.reuse.software/info/github.com/kappapiana/anonymize)

Skip to [howto python](#howto-python)

# ODF and DOCX anonymizer

`anonymize.py` does one thing and hopefully does it well. It allows changing the metadata to comment and track changes and hopefully other metadata in a document.

For those better used to `bash` scripts or cannot install python, `anonymize.sh` is an old and not actively developed (probably broken) version. Use at your own risk (just like the rest, anyway ;-)

## Rationale

The idea came from working as an editor of a peer-reviewed journal (see https://jolts.world), where I needed to remove names of peer-reviewers.

Reviews are half-blind and are done in ODT via Libreoffice, as a preference. However,
the best way to provide feedback -- redlines and comment -- expose the reviewer's name. It is possible to change the settings in Libreoffice, but out of experience very few care (even if properly instructed). Or they realize it halfway through, when it's too late. Full anonymization as Word does (very convoluted) is also unsatisfactory, as you want to retain which of the reviewers suggested a change, maybe for further iterations.

Therefore I needed something to sanitize the data, by changing the names to something like "Reviewer 1" or to consolidate them into a single name.

## Second thought

As a lawyer, I frequently do the same with clients. I change something, clients change something, but we don't want to make it transparent to the other party when we exchange the document. So I want to consolidate my edits and clients'.

If you put the two under the same name, they get automagically consolidated. So you have one single contributor for your edits, and anybody else remains visible.

This is the second option.

## Third thought, docx

I also needed something to clean up the mess of multiple internal edits with many (most) clients who work in docx. Therefore I have added the same functions (also OOXML is a bunch of XML, files zipped together, just a bit more clumsy) for that file type, without the need to convert them in ODT as I used to do before (round robin tends to screw up).

So it will also work with docx (OOXML text document), although MS Word® has a feature to change data as an afterthought (but all or none, AFAICT) so this script might not be strictly necessary (I think it is).

## Fourth thought, python3

Since scripting is limited, I decided to port everything to python3, actually everything has been rewritten with some more sense. It should work for any operating system, as I have abstracted the paths via the `os` library. Hopefully. See [Windows and Mac](#windows-and-mac) for more instructions.


# HOWTO python

It should be sufficient to have a running python3 environment. The imported libraries are all from the standard set.

Run

```shell
[script_directory]/anonymize.py filename.[odt|docx]
```

from any directory and it should produce a copy with `_anon_` prepended to the filename.

Use

```shell
[script_directory]/anonymize.py --help
```

to see other arguments that can be passed to the program.


## TODO

- [ ] remove also document creator, for full anonymization (now only redline and comments creators)

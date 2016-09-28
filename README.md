# RimTranslate
Tool for translation game [RimWorld](http://rimworldgame.com/). It generates standard Gettext PO files for easy translation workflow and maintaining.

## Reasons to use RimTranslate
### Workflow

```
Original Def XML -> PO file -> Translated InjDef XML
                       ^
                   Translator
```
As with the translation of any text or programs in the process of translation RimWorld inevitably run the risk of obsolescence of translated data. It may come out a new version in which new messages appear or change old ones. In such cases it is difficult to track changes and make corrections. With time and the growth of translated data, the complexity will only increase. In addition to this, the translator usually is not can see at once original and translation - they are stored in different files, and to compare them, you may need a lot of time.

To simplify this process, commonly used practice is to use intermediate format, which provides translation relevance and combines both the original and translated messages. RimTranslate uses open format Gettext, widely used by opensource projects. This format is supported by a number of specialized programs for translators, such as poedit (Linux, OS X, Windows) or lokalize (Linux).

Through this approach, the translator does not have to manually keep track of changes after the upgrade program, it is enough to update the translation files PO. Changes, if any, will be immediately visible. After the translation of the update is enough to run RimTransalate again, and XML-files will be updated automatically. It's simple!

## Installation
For running RimTranslate you need following dependencies:

* Python 3.x (tested on 3.4)
  * [polib library](https://bitbucket.org/izi/polib/wiki/Home)
  * [lxml library](http://lxml.de/)

### Installing on Debian/Ubuntu

```apt-get install python3 python3-polib python3-lxml```

## Usage

### First Run

After installation you need to run initialization process, which generates clean PO-files. Here is command (one line):

> ```python RimTranslate.py -s "C:\games\Steam\SteamApps\common\RimWorld\Mods\Core\Defs\" -p "C:\RimWorld_translate\po"```

As you can see, for now you need only two options: `-s` (directory where resides original Def's) and `-p` (directory, where will be placed PO-files).

After that in directory `C:\RimWorld_translate\po` you will see subdirectories with generated PO-files (structure of directories follows to structure of original Defs). As noted above, there exists numbers of programs on various platforms for editing such files. You can even edit them in simple text editor (but is better to use special program to avoid possible errors in format).

### Generating translated files

For generating a translated file you need at least an one translated message in PO-file. Just run:

> ```python RimTranslate.py -o "C:\RimWorld_translate\output" -p "C:\RimWorld_translate\po"```

After that in directory `C:\RimWorld_translate\output` you will see subdirectories with generated files. These subdirectories can be copied into DefInj catalog of your Language Mod for playing and testing in-game.

### Actualization

When comes out new version of game with new messages, simply repeat the two previous commands. For convenience, these two commands can be combined:

> ```python RimTranslate.py -s "C:\games\Steam\SteamApps\common\RimWorld\Mods\Core\Defs\" -p "C:\RimWorld_translate\po" -o "C:\RimWorld_translate\output"```

If the original message has not changed, the translation will remain intact in the PO-file (files are not replaced, but updated) and will move safely to the translated XML-file. If any message has been deleted in the original, it will also be deleted and in translation as obsolete.

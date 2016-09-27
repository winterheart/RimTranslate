#!/usr/bin/python

import os
import re
from lxml import etree
import polib
import argparse
import datetime

parser = argparse.ArgumentParser(description='Creating Gettext PO files and DefInjections for RimWorld translations.')
parser.add_argument('--source-dir', '-s',   action='store', type=str, required=True, help='Root source dir where all Defs (ex. ~/.local/share/Steam/SteamApps/common/RimWorld/Mods/Core/Defs/)')
parser.add_argument('--po-dir',     '-p',   action='store', type=str, required=True, help='Dir where will be placed PO files')
parser.add_argument('--output-dir', '-o',   action='store', type=str, required=True, help='Output dir')

args = parser.parse_args()

# Add trailing slash for sure
args.source_dir = os.path.join(args.source_dir, '')

labels = [
    'beginLetter',
    'beginLetterLabel',
    'description',
    'fixedName',
    'gerund',
    'helpText',
    'inspectLine',
    'label',
    'letterLabel',
    'letterText',
    'pawnLabel',
    'pawnsPlural',
    'rulesStrings',         # hard one
    'recoveryMessage',
    'reportString',
    'skillLabel',
    'text',
    'verb',
]

defNames = [
    'defName',
    'DefName',  # Some DefNames with first uppercase letter
]


def create_pot_file(filename):
    """Create POT file (only source strings exists) from given filename"""
    doc = etree.parse(filename)
    po = polib.POFile()
    [undef, basefile] = filename.split(args.source_dir, 1)
    po.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'you@example.com',
        'POT-Creation-Date': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
        'PO-Revision-Date': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
        'Last-Translator': 'Some Translator <yourname@example.com>',
        'Language-Team': 'English <yourteam@example.com>',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }
    po.metadata_is_fuzzy = 1

    for defName in defNames:
        for defName_node in doc.findall("//" + defName):
            if defName_node is not None:
                parent = defName_node.getparent()
                print("  Found defName '%s' (%s)" % (defName_node.text, doc.getpath(parent)))
                for label in labels:
                    parent = defName_node.getparent()
                    print ("  Checking label %s" % (label))
                    label_nodes = parent.findall(".//" + label)
                    for label_node in label_nodes:
                        print("  Found Label '%s' (%s)" % (label, doc.getpath(label_node)))

                        # Generate string for parenting
                        [undef, path_label] = doc.getpath(label_node).split(doc.getpath(parent), 1)
                        path_label = re.sub(r'\/', '.', path_label)
                        path_label = re.sub(r'\.li\.', '.0.', path_label)
                        match = re.search(r'\.li\[(\d+)\]\.', path_label)
                        if match:
                            path_label = re.sub(r'\.li\[\d+\]\.', "." + str(int(match.group(1)) - 1) + ".", path_label)
                        print("  msgctxt: " + defName_node.text + path_label)

                        entry = polib.POEntry(
                            msgctxt=defName_node.text + path_label,
                            msgid=label_node.text,
                            occurrences=[(basefile, str(label_node.sourceline))]
                        )
                        po.append(entry)
    # sort by line in source file
    po.sort(key=lambda x: int(x.occurrences[0][1]))

    return po


def create_translation_file(po_file):
    languagedata = etree.Element('LanguageData')
    xml = etree.ElementTree(languagedata)
    po = polib.pofile(po_file)
    for po_entry in po:
        if (po_entry.msgstr != "") and ('fuzzy' not in po_entry.flags):
            print(po_entry.msgctxt)
            entry = etree.SubElement(languagedata, po_entry.msgctxt)
            entry.text = str(po_entry.msgstr)
    outfile = open('out.xml', 'w')
    # Hack - silly lxml cannot write native unicode strings
    outfile.write(etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8'))
    return 0


for root, dirs, files in os.walk(args.source_dir):
    for dir in dirs:
        full_filename = os.path.join(root, dir)
        [udnef, filedir] = full_filename.split(args.source_dir, 1)
        # Create po directory structure
        po_full_filename = os.path.join(args.po_dir, filedir)
        if not(os.path.exists(po_full_filename)):
            os.makedirs(po_full_filename)

        # Create InjDefs directory structure
        output_full_filename = os.path.join(args.output_dir, filedir)
        if not(os.path.exists(output_full_filename)):
            os.makedirs(output_full_filename)

    for file in files:
        if file.endswith('.xml'):
            full_filename = os.path.join(root,file)
            print("Processing " + full_filename)

            [undef, filedir] = full_filename.split(args.source_dir, 1)
            pot = create_pot_file(full_filename)
            pofilename = os.path.join(args.po_dir, filedir)

            if os.path.exists(pofilename + ".po"):
                print("  Updating PO file " + pofilename + ".po")
                po = polib.pofile(pofilename + ".po")
                po.merge(pot)
                po.save(pofilename + ".po")
            else:
                print("  Creating PO file " + pofilename + ".po")
                pot.save(pofilename + ".po")

create_translation_file('po/SkillDefs/Skills.xml.po')

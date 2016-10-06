#!/usr/bin/python

import os
import re
from lxml import etree
import polib
import argparse
import datetime
import logging

version = "0.6.0"

parser = argparse.ArgumentParser(description='RimTranslate.py v%s - Creating Gettext PO files and DefInjections for RimWorld translations.' % version,
                                 epilog='This is free software that licensed under GPL-3. See LICENSE for more info.',
                                 formatter_class=argparse.RawTextHelpFormatter)

group_source = parser.add_argument_group('Extracting options')
group_source.add_argument('--source-dir', '-s', type=str,
                          help='''Root source dir where all Defs (ex. ~/.local/share/Steam/SteamApps/common/RimWorld/Mods/Core/Defs/)''')

group_generation = parser.add_argument_group('Generation options')
group_generation.add_argument('--output-dir', '-o', type=str,
                              help='Directory where will be placed InjDefs XML-files with actual translations')

parser.add_argument('--po-dir', '-p', type=str,
                    help='Directory where will be placed generated or updated PO-files')

parser.add_argument('--compendium', '-c', type=str,
                    help='Directory that conains already translated InjDefs XML files for generating compedium and using it as translation memory')

parser.add_argument('-v', type=str, default='ERROR',
                    help='Enable verbose output (debug, info, warning, error, critical)')

args = parser.parse_args()

if not ((args.output_dir or args.source_dir) and args.po_dir):
    parser.error('''No action requested. The following arguments are required:
  "--source-dir <SOURCE_DIR> --po-dir <PO_DIR>"
  or
  "--output-dir <SOURCE_DIR> --po-dir <PO_DIR>"''')

if os.path.exists('RimTranslate.log'):
    os.remove('RimTranslate.log')

log_level = getattr(logging, str.upper(args.v))
logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level, filename='RimTranslate.log')
console = logging.StreamHandler()
console.setLevel(log_level)
console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logging.getLogger('').addHandler(console)

# Add trailing slash for sure
if args.source_dir:
    args.source_dir = os.path.join(args.source_dir, '')
if args.po_dir:
    args.po_dir = os.path.join(args.po_dir, '')
if args.output_dir:
    args.output_dir = os.path.join(args.output_dir, '')


labels = [
    'beginLetter',
    'beginLetterLabel',
    'description',
    'fixedName',
    'gerund',
    'helpText',
    'ingestCommandString',
    'ingestReportString',
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


def generate_definj_xml_tag(string):
    """Create XML tag for InjectDefs"""
    string = re.sub(r'/', '.', string)
    string = re.sub(r'\.li\.', '.0.', string)
    string = re.sub(r'\.li$', '.0', string)
    match = re.search(r'\.li\[(\d+)\]', string)
    if match:
        string = re.sub(r'\.li\[\d+\]', "." + str(int(match.group(1)) - 1), string)

    return string


def create_compendium_from_definj(filename):
    """Create compendium from already created definj XML files"""
    po_file = polib.POFile()
    doc = etree.parse(filename)
    for languageData in doc.xpath('//LanguageData'):
        for element in languageData:
            if element.tag is not etree.Comment():
                entry = polib.POEntry(
                    msgctxt=element.tag,
                    msgid=element.tag,
                    msgstr=element.text
                )
            po_file.append(entry)

    return po_file



def create_pot_file_from_def(filename):
    """Create POT file (only source strings exists) from given filename"""
    doc = etree.parse(filename)
    po_file = polib.POFile()
    basefile = filename.split(args.source_dir, 1)[1]
    po_file.metadata = {
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
    po_file.metadata_is_fuzzy = 1

    for defName in defNames:
        for defName_node in doc.findall("//" + defName):
            if defName_node is not None:
                parent = defName_node.getparent()
                logging.debug("Found defName '%s' (%s)" % (defName_node.text, doc.getpath(parent)))
                for label in labels:
                    parent = defName_node.getparent()
                    logging.debug("Checking label %s" % label)
                    label_nodes = parent.findall(".//" + label)
                    for label_node in label_nodes:
                        logging.debug("Found Label '%s' (%s)" % (label, doc.getpath(label_node)))
                        if len(label_node):
                            logging.debug("Element has children")
                            for child_node in label_node:
                                if child_node.tag is not etree.Comment:
                                    path_label = doc.getpath(child_node).split(doc.getpath(parent), 1)[1]
                                    path_label = generate_definj_xml_tag(path_label)
                                    logging.debug("msgctxt: " + defName_node.text + path_label)

                                    entry = polib.POEntry(
                                        msgctxt=defName_node.text + path_label,
                                        msgid=child_node.text,
                                        occurrences=[(basefile, str(child_node.sourceline))]
                                    )
                                    po_file.append(entry)
                        else:
                            # Generate string for parenting
                            path_label = doc.getpath(label_node).split(doc.getpath(parent), 1)[1]
                            path_label = generate_definj_xml_tag(path_label)
                            logging.debug("msgctxt: " + defName_node.text + path_label)

                            entry = polib.POEntry(
                                msgctxt=defName_node.text + path_label,
                                msgid=label_node.text,
                                occurrences=[(basefile, str(label_node.sourceline))]
                            )
                            po_file.append(entry)
    # sort by line in source file
    po_file.sort(key=lambda x: int(x.occurrences[0][1]))

    return po_file


def create_languagedata_xml_file(po_file):
    languagedata = etree.Element('LanguageData')
    languagedata.addprevious(etree.Comment(' This file autogenerated with RimTranslate.py v%s ' % version))
    languagedata.addprevious(etree.Comment(' https://github.com/winterheart/RimTranslate/ '))
    languagedata.addprevious(etree.Comment(' Don\'t edit this file manually, edit PO file and regenerate this file! '))
    xml = etree.ElementTree(languagedata)
    po = polib.pofile(po_file)
    for po_entry in po:
        if (po_entry.msgstr != "") and ('fuzzy' not in po_entry.flags):
            entry = etree.SubElement(languagedata, po_entry.msgctxt)
            entry.text = str(po_entry.msgstr)
    # Hack - silly lxml cannot write native unicode strings
    xml_file = etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8')
    return xml_file

if args.compendium:
    logging.info('Creating compendium from already exist DefInj XML files')
    if os.path.isdir(args.compendium):
        compendium = polib.POFile()
        for root, dirs, files in os.walk(args.compendium):
            for file in files:
                if file.endswith('.xml'):
                    full_filename = os.path.join(root, file)
                    logging.debug('Processing %s for compendium' % full_filename)
                    compendium += create_compendium_from_definj(full_filename)
    else:
        logging.error('%s is not directory or does not exists!' % args.compendium)


if args.source_dir:
    logging.info('Beginning to generate PO-files')
    if os.path.isdir(args.source_dir):
        for root, dirs, files in os.walk(args.source_dir):
            for file in files:
                if file.endswith('.xml'):
                    full_filename = os.path.join(root, file)
                    logging.info("Processing " + full_filename)
                    file_dir = full_filename.split(args.source_dir, 1)[1]

                    pot = create_pot_file_from_def(full_filename)
                    pofilename = os.path.join(args.po_dir, file_dir)
                    pofilename += '.po'

                    if os.path.exists(pofilename):
                        logging.info("Updating PO file " + pofilename)
                        po = polib.pofile(pofilename)
                        po.merge(pot)
                    else:
                        # Is there some useful info?
                        if len(pot) > 0:
                            directory = os.path.dirname(pofilename)
                            if not(os.path.exists(directory)):
                                logging.info("Creating directory " + directory)
                                os.makedirs(directory)
                            logging.info("Creating PO file " + pofilename)
                        po = pot

                    # If there compendium, fill entries with transaltaion memory
                    if args.compendium:
                        for entry in po:
                            if entry.msgstr == '':
                                check_msg = compendium.find(entry.msgctxt, by='msgctxt', include_obsolete_entries=False)
                                if check_msg:
                                    entry.msgstr = check_msg.msgstr
                                    if 'fuzzy' not in entry.flags:
                                        entry.flags.append('fuzzy')
                    if len(po):
                        po.save(pofilename)

    else:
        logging.error('%s is not directory or does not exists!' % args.source_dir)
        quit()

if args.output_dir:
    logging.info('Beginning to generate DefInjected files')
    for root, dirs, files in os.walk(args.po_dir):
        for file in files:
            if file.endswith('.po'):
                full_filename = os.path.join(root, file)
                logging.info("Processing " + full_filename)
                xml_filename = full_filename.split(args.po_dir, 1)[1]
                xml_filename = xml_filename.strip('.po')
                xml_filename = os.path.join(args.output_dir, xml_filename)
                directory = os.path.dirname(xml_filename)

                po = polib.pofile(full_filename)
                # Do we have translated entries?
                if len(po.translated_entries()) > 0:
                    if not (os.path.exists(directory)):
                        logging.info("Creating directory " + directory)
                        os.makedirs(directory)
                    logging.info("Creating XML file " + pofilename)
                    xml_content = create_languagedata_xml_file(full_filename)
                    target = open(xml_filename, 'w')
                    target.write(xml_content)
                    target.close()

import datetime
from lxml import etree
import polib
import re

from logger import Logger

def create_pot_file(category, filename, source_dir, compendium, compendium_mode=False):
    if category == 'DefInjected':
        return create_pot_file_from_def(filename, source_dir)
    elif category == 'Keyed':
        return create_pot_file_from_keyed(filename, source_dir, compendium, compendium_mode)
    else:
        Logger.logger.error('Incorrect pot file category requested: %s' % category)
        quit()

def create_pot_file_from_keyed(filename, source_dir, compendium, compendium_mode=False):
    """Create compendium from keyed or already created definj XML files"""
    parser = etree.XMLParser(remove_comments=True)
    if compendium:
        basefile = 'compendium'
    else:
        basefile = filename.split(source_dir, 1)[1]

    po_file = polib.POFile()
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
    doc = etree.parse(filename, parser)
    for languageData in doc.xpath('//LanguageData'):
        for element in languageData:
            entry = polib.POEntry(
                msgctxt=element.tag,
                msgid=element.text,
                occurrences=[(basefile, str(element.sourceline))]
            )
            if compendium_mode:
                entry.msgstr = element.text
            po_file.append(entry)

    return po_file


def create_pot_file_from_def(filename, source_dir):
    """Create POT file (only source strings exists) from given filename"""
    doc = etree.parse(filename)
    po_file = polib.POFile()
    basefile = filename.split(source_dir, 1)[1]

    # TODO: put this in config
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

    defNames = [
        'defName',
        'DefName',  # Some DefNames with first uppercase letter
    ]

    labels = [
        'beginLetter',
        'beginLetterLabel',
        'description',
        'fixedName',
        'gerund',
        'gerundLabel',
        'helpText',
        'ingestCommandString',
        'ingestReportString',
        'inspectLine',
        'label',
        'labelShort',
        'letterLabel',
        'letterText',
        'pawnLabel',
        'pawnsPlural',
        'rulesStrings',         # hard one
        'recoveryMessage',
        'reportString',
        'skillLabel',
        'text',
        'useLabel',
        'verb',
    ]

    for defName in defNames:
        for defName_node in doc.findall(".//" + defName):
            if defName_node is not None:
                parent = defName_node.getparent()
                Logger.logger.debug("Found defName '%s' (%s)" % (defName_node.text, doc.getpath(parent)))
                for label in labels:
                    parent = defName_node.getparent()
                    Logger.logger.debug("Checking label %s" % label)
                    label_nodes = parent.findall(".//" + label)
                    for label_node in label_nodes:
                        Logger.logger.debug("Found Label '%s' (%s)" % (label, doc.getpath(label_node)))
                        if len(label_node):
                            Logger.logger.debug("Element has children")
                            for child_node in label_node:
                                if child_node.tag is not etree.Comment:
                                    path_label = doc.getpath(child_node).split(doc.getpath(parent), 1)[1]
                                    path_label = generate_definj_xml_tag(path_label)

                                    Logger.logger.debug("msgctxt: " + defName_node.text + path_label)
                                    entry = polib.POEntry(
                                        msgctxt=defName_node.text + path_label,
                                        msgid=child_node.text,
                                        occurrences=[(basefile, str(label_node.sourceline))]
                                    )
                                    po_file.append(entry)
                        else:
                            # Generate string for parenting
                            path_label = doc.getpath(label_node).split(doc.getpath(parent), 1)[1]
                            path_label = generate_definj_xml_tag(path_label)

                            Logger.logger.debug("msgctxt: " + defName_node.text + path_label)

                            if not label_node.text:
                                Logger.logger.warning(path_label + " has 'None' message!")
                            else:
                                entry = polib.POEntry(
                                    msgctxt=defName_node.text + path_label,
                                    msgid=label_node.text,
                                    occurrences=[(basefile, str(label_node.sourceline))]
                                )
                                po_file.append(entry)
    # sort by line in source file
    po_file.sort(key=lambda x: int(x.occurrences[0][1]))

    return po_file

def generate_definj_xml_tag(string):
    """Create XML tag for InjectDefs"""
    string = re.sub(r'/', '.', string)
    string = re.sub(r'\.li\.', '.0.', string)
    string = re.sub(r'\.li$', '.0', string)
    match = re.search(r'\.li\[(\d+)\]', string)
    if match:
        string = re.sub(r'\.li\[\d+\]', "." + str(int(match.group(1)) - 1), string)

    return string

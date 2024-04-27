import os
import polib

from Helpers import create_pot_file_from_keyed, create_pot_file_from_def, create_languagedata_xml_file, create_logger
from Parser import parse_arguments

class Translator:
    def __init__(self):
        self.args = parse_arguments()
        self.logger = create_logger(self.args.v)

        # TODO: move log into a new log/ folder
        if os.path.exists('RimTranslate.log'):
            os.remove('RimTranslate.log')

    def start(self):
        if self.args.source_dir:
            self.build_source_dir()
        if self.args.output_dir:
            self.build_output_dir()

    def build_compendium(self):
        self.logger.info('Creating compendium from already exist DefInj XML files')

        if os.path.isdir(self.args.compendium):
            compendium = polib.POFile()
            for root, dirs, files in os.walk(self.args.compendium):
                for file in files:
                    if file.endswith('.xml'):
                        full_filename = os.path.join(root, file)
                        self.logger.debug('Processing %s for compendium' % full_filename)
                        compendium += create_pot_file_from_keyed(full_filename, self.args.source_dir, self.args.compendium, True)

            return compendium
        else:
            self.logger.error('%s is not directory or does not exists!' % self.args.compendium)

    def build_source_dir(self):
        compendium = self.build_compendium()

        self.logger.info('Beginning to generate PO-files')

        self.logger.info('Generating PO-files from Defs')
        # Parse Defs subdirectory
        defs_source_dir = os.path.join(self.args.source_dir, 'Defs', '')

        if os.path.isdir(defs_source_dir):
            for root, dirs, files in os.walk(defs_source_dir):
                for file in files:
                    if file.endswith('.xml'):
                        full_filename = os.path.join(root, file)
                        self.logger.info("Processing " + full_filename)
                        file_dir = full_filename.split(defs_source_dir, 1)[1]
                        # Replace Defs to Def, issue #1
                        file_dir = file_dir.replace("Defs", "Def")

                        pot = create_pot_file_from_def(full_filename, self.args.source_dir)
                        pofilename = os.path.join(self.args.po_dir, 'DefInjected', file_dir)
                        pofilename += '.po'

                        if os.path.exists(pofilename):
                            self.logger.info("Updating PO file " + pofilename)
                            po = polib.pofile(pofilename)
                            po.merge(pot)
                        else:
                            # Is there some useful info?
                            if len(pot) > 0:
                                directory = os.path.dirname(pofilename)
                                if not(os.path.exists(directory)):
                                    self.logger.info("Creating directory " + directory)
                                    os.makedirs(directory)
                                self.logger.info("Creating PO file " + pofilename)
                            po = pot

                        # If there compendium, fill entries with translation memory
                        if self.args.compendium:
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
            self.logger.error('%s is not directory or does not exists!' % defs_source_dir)
            quit()

        self.logger.info('Generating PO-files from Keyed')
        # Parse Language/English/Keyed
        keyed_source_dir = os.path.join(self.args.source_dir, 'Languages/English/Keyed', '')

        # Processing Keyed folder
        if os.path.isdir(keyed_source_dir):
            for root, dirs, files in os.walk(keyed_source_dir):
                for file in files:
                    if file.endswith('.xml'):
                        full_filename = os.path.join(root, file)
                        self.logger.info("Processing " + full_filename)
                        file_dir = full_filename.split(keyed_source_dir, 1)[1]

                        pot = create_pot_file_from_keyed(full_filename, self.args.source_dir, self.args.compendium)
                        pofilename = os.path.join(self.args.po_dir, 'Keyed', file_dir)
                        pofilename += '.po'

                        if os.path.exists(pofilename):
                            self.logger.info("Updating PO file " + pofilename)
                            po = polib.pofile(pofilename)
                            po.merge(pot)
                        else:
                            # Is there some useful info?
                            if len(pot) > 0:
                                directory = os.path.dirname(pofilename)
                                if not (os.path.exists(directory)):
                                    self.logger.info("Creating directory " + directory)
                                    os.makedirs(directory)
                                self.logger.info("Creating PO file " + pofilename)
                            po = pot

                        # If there compendium, fill entries with translation memory
                        if self.args.compendium:
                            for entry in po:
                                if entry.msgstr == '':
                                    check_msg = compendium.find(entry.msgctxt, by='msgctxt', include_obsolete_entries=False)
                                    if check_msg and check_msg.msgstr:
                                        entry.msgstr = check_msg.msgstr
                                        if 'fuzzy' not in entry.flags:
                                            entry.flags.append('fuzzy')
                        if len(po):
                            po.save(pofilename)
        else:
            self.logger.error('%s is not directory or does not exists!' % keyed_source_dir)
            quit()

    def build_output_dir(self):
        self.logger.info('Beginning to generate DefInjected files')
        fuzzy = 0
        total = 0
        translated = 0
        untranslated = 0

        for root, dirs, files in os.walk(self.args.po_dir):
            for file in files:
                if file.endswith('.po'):
                    full_filename = os.path.join(root, file)
                    self.logger.info("Processing " + full_filename)
                    xml_filename = full_filename.split(self.args.po_dir, 1)[1]
                    xml_filename = xml_filename.strip('.po')
                    xml_filename = os.path.join(self.args.output_dir, xml_filename)
                    directory = os.path.dirname(xml_filename)

                    po = polib.pofile(full_filename)
                    translated_po_entries = len(po.translated_entries())
                    fuzzy_po_entries = len(po.fuzzy_entries())
                    untranslated_po_entries = len(po.untranslated_entries())

                    translated = translated + translated_po_entries
                    fuzzy = fuzzy + fuzzy_po_entries
                    untranslated = untranslated + untranslated_po_entries

                    # Do we have translated entries?
                    if translated_po_entries > 0:
                        if not (os.path.exists(directory)):
                            self.logger.info("Creating directory " + directory)
                            os.makedirs(directory)
                        xml_content = create_languagedata_xml_file(full_filename)
                        target = open(xml_filename, "w", encoding="utf8")
                        target.write(xml_content)
                        target.close()
                    total_po_entries = len([e for e in po if  not e.obsolete])
                    total = total + total_po_entries

        print("Statistics (untranslated/fuzzy/translated/total): %d/%d/%d/%d" % (untranslated, fuzzy, translated, total))


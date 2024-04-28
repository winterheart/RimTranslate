import os
import polib

from Helpers import create_pot_file, create_pot_file_from_keyed, create_languagedata_xml_file, create_logger, merge_compendium
from Parser import parse_arguments
from source_dir_builder import SourceDirBuilder

class Translator:
    def __init__(self):
        self.args = parse_arguments()
        self.logger = create_logger(self.args.v)
        self.compendium = None

        if self.args.compendium:
            self.compendium = self.build_compendium()

        # TODO: move log into a new log/ folder
        if os.path.exists('RimTranslate.log'):
            os.remove('RimTranslate.log')

    def start(self):
        if self.args.source_dir:
            SourceDirBuilder(self.args, self.compendium, self.logger).build_source_dir()
        if self.args.output_dir:
            self.build_output_dir()

    def build_compendium(self):
        if self.compendium is not None:
            self.logger.warn('Compendium already built; skipping.')
            return self.compendium

        self.logger.info('Creating compendium from already exist DefInj XML files')

        if not os.path.isdir(self.args.compendium):
            self.logger.error('%s is not directory or does not exists!' % self.args.compendium)
            quit()

        compendium = polib.POFile()

        for root, dirs, files in os.walk(self.args.compendium):
            for file in files:
                if file.endswith('.xml'):
                    full_filename = os.path.join(root, file)
                    self.logger.debug('Processing %s for compendium' % full_filename)
                    compendium += create_pot_file_from_keyed(full_filename, self.args.source_dir, self.args.compendium, True)

        return compendium

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


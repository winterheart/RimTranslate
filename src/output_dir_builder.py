import os
import polib

from Helpers import create_languagedata_xml_file

class OutputDirBuilder():
    def __init__(self, args, logger):
        self.args = args
        self.logger = logger

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


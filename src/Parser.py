import argparse

# TODO: this is also in main file
version = "0.6.7"

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='RimTranslate.py v%s - Creating Gettext PO files and DefInjections for RimWorld translations.' % version,
        epilog='This is free software that licensed under GPL-3. See LICENSE for more info.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    group_source = parser.add_argument_group('Extracting options')
    group_source.add_argument(
        '--source-dir', '-s', type=str,
        help='''Root source dir where all Defs and Keyed files (ex. ~/.local/share/Steam/SteamApps/common/RimWorld/Mods/Core/)'''
    )

    group_generation = parser.add_argument_group('Generation options')
    group_generation.add_argument(
        '--output-dir', '-o', type=str,
        help='Directory where will be placed InjDefs XML-files with actual translations'
    )

    parser.add_argument(
        '--po-dir', '-p', type=str,
        help='Directory where will be placed generated or updated PO-files'
    )

    parser.add_argument(
        '--compendium', '-c', type=str,
        help='Directory that conains already translated InjDefs XML files for generating compendium and using it as translation memory'
    )

    # TODO: change default level to WARNING
    # TODO: change help message to use all caps values (e.g. DEBUG)
    parser.add_argument(
        '-v', type=str, default='ERROR',
        help='Enable verbose output (debug, info, warning, error, critical)'
    )

    args = parser.parse_args()

    # TODO: do we need this? I don't think so. argparse reports usage anyway
    #       but then it's nice to have extra guidance
    #  if not ((args.output_dir or args.source_dir) and args.po_dir):
    #      parser.error('''
    #          No action requested. The following arguments are required:
    #          "--source-dir <SOURCE_DIR> --po-dir <PO_DIR>"
    #          or
    #          "--output-dir <SOURCE_DIR> --po-dir <PO_DIR>"
    #      ''')

    # Add trailing slash for sure
    if args.source_dir:
        args.source_dir = os.path.join(args.source_dir, '')
    if args.po_dir:
        args.po_dir = os.path.join(args.po_dir, '')
    if args.output_dir:
        args.output_dir = os.path.join(args.output_dir, '')

    return parser, args

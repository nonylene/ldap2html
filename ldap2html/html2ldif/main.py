import ldap3
import sys
import argparse
import logging
import traceback
from pathlib import Path
import os

from .config import Config
from .convert import to_ldap_entries


def html2ldif(config: Config):
    directory = Path(config.target_directory) / config.domain

    for path in config.files:
        try:
            html = open(path).read()
            html_path = os.path.join(config.base_directory, Path(path).name)
            print(html_path)

            entries = to_ldap_entries(html, config.domain, html_path)
            logging.debug(entries)

            conn = ldap3.Connection(server=None, client_strategy=ldap3.LDIF)
            conn.open()

            ldif_path = directory / f"{html_path}.ldif"
            ldif_path.parent.mkdir(parents=True, exist_ok=True)
            with open(ldif_path, "w") as f:
                for entry in entries:
                    ldif = conn.add(entry.dn, entry.object_class(), entry.attributes())
                    if not config.modify:
                        ldif = ldif.replace('changetype: add\n', '')
                    f.write(f'{ldif}\n\n')

        except Exception:
            print(f"Failed to process file: {path}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Convert LDAP entries to HTML file')
    parser.add_argument('-n', '--domain', dest='domain', type=str, required=True, help="Domain name for HTML files")
    parser.add_argument('-d', '--dir', dest='target_directory', type=str, default='out/ldif',
                        help="Target directory to save files. Default value is out/ldif.")
    parser.add_argument('-b', '--basedir', dest='base_directory', type=str, default='',
                        help="Base (prefix) directory for html files.")
    parser.add_argument('-m', '--modify', dest='modify', action='store_true', help="Generate LDIF for ldapmodify")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help="Verbose output")
    parser.add_argument('file', type=str, nargs='+', help="HTML files")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    config = Config(
        args.domain, args.target_directory, args.base_directory, args.modify, args.file
    )

    html2ldif(config)

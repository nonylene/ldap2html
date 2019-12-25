import ldap3
import sys
import argparse
import logging
import traceback
from pathlib import Path

from ..ldap.model import LdapHtmlFile
from ..ldap import model as ldap_model
from ..ldap.utils import search
from .config import Config
from .convert import to_html_file


def ldap2html(config: Config):
    directory = Path(config.directory)

    server = ldap3.Server(config.ldap_uri, get_info=ldap3.ALL)
    conn = ldap3.Connection(server, config.bind_dn, config.bind_dn_passwd, auto_bind=True)

    html_file_filter = f'(objectClass={ldap_model.OBJECT_CLASS_HTML_FILE})'

    for l_html_file in search(conn, config.search_base, html_file_filter, LdapHtmlFile):
        try:
            html_file = to_html_file(conn, l_html_file)
            logging.debug(html_file)

            html = html_file.to_html()
            path = directory / html_file.filename
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(html)
        except Exception:
            print(f"Failed to process file: {l_html_file}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Convert LDAP entries to HTML file')
    parser.add_argument('-H', '--uri', dest='ldap_uri', type=str, default="ldap://localhost", help="LDAP uri")
    parser.add_argument('-b', '--searchbase', dest='search_base', type=str, required=True, help="LDAP search base")
    parser.add_argument('-D', '--binddn', dest='bind_dn', type=str, required=True, help="LDAP bind dn")
    parser.add_argument('-w', '--passwd', dest='bind_dn_passwd', type=str, required=True, help="LDAP bind dn password")
    parser.add_argument('-d', '--dir', dest='directory', type=str, default='out/html',
                        help="Target directory to save files. Default value is out/html.")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    config = Config(
        args.ldap_uri, args.search_base, args.bind_dn, args.bind_dn_passwd,
        args.directory
    )

    ldap2html(config)

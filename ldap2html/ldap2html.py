import ldap3
import sys
import traceback
from pathlib import Path
import logging

from .ldap.model import LdapHtmlFile
from .ldap import model as ldap_model
from .ldap.utils import search
from .config import Config
from .convert import to_html_file


def ldap2html(config: Config):
    directory = Path(config.directory)
    directory.mkdir(parents=True, exist_ok=True)

    server = ldap3.Server(config.ldap_uri, get_info=ldap3.ALL)
    conn = ldap3.Connection(server, config.bind_dn, config.bind_dn_passwd, auto_bind=True)

    html_file_filter = f'(objectClass={ldap_model.OBJECT_CLASS_HTML_FILE})'

    for l_html_file in search(conn, config.search_base, html_file_filter, LdapHtmlFile):
        try:
            html_file = to_html_file(conn, l_html_file)
            logging.debug(html_file)

            html = html_file.to_html()
            with open(directory / html_file.filename, "w") as f:
                f.write(html)
        except Exception:
            print(f"Failed to process file: {l_html_file}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)

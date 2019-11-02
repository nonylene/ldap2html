import ldap3
import sys
import traceback

from .ldap.model import LdapHtmlFile
from .ldap import model as ldap_model
from .ldap.utils import search
from .convert import to_html_file

LDAP_HOST = 'localhost'

SEARCH_BASE_DOMAIN = 'dc=example,dc=com'
BIND_DN = f'cn=admin,{SEARCH_BASE_DOMAIN}'
BIND_DN_PASS = 'admin'

server = ldap3.Server(LDAP_HOST, get_info=ldap3.ALL)
conn = ldap3.Connection(server, BIND_DN, BIND_DN_PASS, auto_bind=True)

html_file_filter = f'(objectClass={ldap_model.OBJECT_CLASS_HTML_FILE})'
html_element_filter = f'(objectClass={ldap_model.OBJECT_CLASS_HTML_ELEMENT})'

for l_html_file in search(conn, SEARCH_BASE_DOMAIN, html_file_filter, LdapHtmlFile):
    try:
        html_file = to_html_file(conn, l_html_file)
        html = html_file.to_html()
        with open(html_file.filename, "w") as f:
            f.write(html)
    except Exception:
        print(f"Failed to process file: {l_html_file}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

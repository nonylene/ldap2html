import argparse

from ldap2html.config import Config
from ldap2html.ldap2html import ldap2html

parser = argparse.ArgumentParser(description='Convert LDAP entries to HTML file')
parser.add_argument('-H', '--uri', dest='ldap_uri', type=str, default="ldap://localhost", help="LDAP uri")
parser.add_argument('-b', '--searchbase', dest='search_base', type=str, required=True, help="LDAP search base")
parser.add_argument('-D', '--binddn', dest='bind_dn', type=str, required=True, help="LDAP bind dn")
parser.add_argument('-w', '--passwd', dest='bind_dn_passwd', type=str, required=True, help="LDAP bind dn password")

args = parser.parse_args()

config = Config(
    args.ldap_uri, args.search_base, args.bind_dn, args.bind_dn_passwd
)

ldap2html(config)

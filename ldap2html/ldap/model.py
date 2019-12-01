from dataclasses import dataclass
from typing import List, Type
import ldap3

# For convertion
ELEMENT_ATTR_DICT = {
    'htmlAttrClass': 'class',
    'htmlAttrLang': 'lang',
    'htmlAttrHref': 'href',
}

# ldap_model definitions must have the same attributes as LDAP schema.
# These classes may be instanced dynamically (see from_ldap_entry()).


@dataclass
class LdapBase:
    dn: str


OBJECT_CLASS_HTML_FILE = 'htmlFile'


@dataclass
class LdapHtmlFile(LdapBase):
    o: List[str]


OBJECT_CLASS_HTML_PARTILCE = 'htmlParticlce'


@dataclass
class LdapHtmlParticle(LdapBase):
    htmlNthChild: List[int]


OBJECT_CLASS_HTML_TEXT = 'htmlText'


@dataclass
class LdapHtmlText(LdapHtmlParticle):
    cn: List[str]
    htmlTextValue: List[bytes]


@dataclass
class LdapHtmlElement(LdapHtmlParticle):
    ou: List[str]
    htmlTagName: List[bytes]
    # attributes
    htmlAttrClass: List[bytes]
    htmlAttrLang: List[bytes]
    htmlAttrHref: List[bytes]


OBJECT_CLASS_HTML_VOID_ELEMENT = 'htmlVoidElement'


@dataclass
class LdapHtmlVoidElement(LdapHtmlElement):
    pass


OBJECT_CLASS_HTML_NORMAL_ELEMENT = 'htmlNormalElement'


@dataclass
class LdapHtmlNormalElement(LdapHtmlElement):
    pass


def from_ldap_entry(entry: ldap3.Entry, cls: Type[LdapBase]) -> LdapBase:
    args = entry.entry_attributes_as_dict
    args["dn"] = entry.entry_dn
    return cls(**args)

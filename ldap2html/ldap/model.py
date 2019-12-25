from dataclasses import dataclass, asdict
from typing import List, Type, Dict
import ldap3

# For convertion
ELEMENT_ATTR_DICT = {
    'htmlAttrClass': 'class',
    'htmlAttrLang': 'lang',
    'htmlAttrHref': 'href',
    'htmlAttrSrc': 'src',
    'htmlAttrAlt': 'alt',
    'htmlAttrWidth': 'width',
}

# ldap_model definitions must have the same attributes as LDAP schema.
# These classes may be instanced dynamically (see from_ldap_entry()).


@dataclass
class LdapBase:
    dn: str

    def object_class(self) -> str:
        raise NotImplementedError()

    def attributes(self) -> Dict[str, List[bytes]]:
        dic = asdict(self)
        del dic['dn']
        return dic


OBJECT_CLASS_HTML_FILE = 'htmlFile'


@dataclass
class LdapHtmlFile(LdapBase):
    o: List[str]

    def object_class(self):
        return OBJECT_CLASS_HTML_FILE


OBJECT_CLASS_HTML_PARTILCE = 'htmlParticlce'


@dataclass
class LdapHtmlParticle(LdapBase):
    htmlNthChild: List[int]

    def object_class(self):
        return OBJECT_CLASS_HTML_PARTILCE


OBJECT_CLASS_HTML_TEXT = 'htmlText'


@dataclass
class LdapHtmlText(LdapHtmlParticle):
    cn: List[str]
    htmlTextValue: List[bytes]

    def object_class(self):
        return OBJECT_CLASS_HTML_TEXT


@dataclass
class LdapHtmlElement(LdapHtmlParticle):
    ou: List[str]
    htmlTagName: List[bytes]
    # attributes
    htmlAttrClass: List[bytes]
    htmlAttrLang: List[bytes]
    htmlAttrHref: List[bytes]
    htmlAttrSrc: List[bytes]
    htmlAttrAlt: List[bytes]
    htmlAttrWidth: List[bytes]


OBJECT_CLASS_HTML_VOID_ELEMENT = 'htmlVoidElement'


@dataclass
class LdapHtmlVoidElement(LdapHtmlElement):

    def object_class(self):
        return OBJECT_CLASS_HTML_VOID_ELEMENT


OBJECT_CLASS_HTML_NORMAL_ELEMENT = 'htmlNormalElement'


@dataclass
class LdapHtmlNormalElement(LdapHtmlElement):

    def object_class(self):
        return OBJECT_CLASS_HTML_NORMAL_ELEMENT


def from_ldap_entry(entry: ldap3.Entry, cls: Type[LdapBase]) -> LdapBase:
    args = entry.entry_attributes_as_dict
    args["dn"] = entry.entry_dn
    return cls(**args)

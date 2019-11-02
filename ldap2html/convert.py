import ldap3

from operator import itemgetter

import itertools

from .ldap.model import LdapHtmlText, LdapHtmlElement, LdapHtmlParticle, LdapHtmlFile
from .ldap import model as ldap_model
from .ldap.utils import search
from .html.model import HtmlElement, HtmlText, HtmlFile

# For convertion
ELEMENT_ATTR_DICT = {
    'htmlAttrClass': 'class',
}

filter_element = f'(objectClass={ldap_model.OBJECT_CLASS_HTML_ELEMENT})'
filter_text = f'(objectClass={ldap_model.OBJECT_CLASS_HTML_TEXT})'


def _get_nth(particle: LdapHtmlParticle) -> int:
    if len(particle.htmlNthChild) == 0:
        return -1
    return particle.htmlNthChild[0]


def to_html_text(l_html_text: LdapHtmlText) -> HtmlText:
    return HtmlText(l_html_text.htmlTextValue[0].decode())


def to_html_element(conn: ldap3.Connection, l_element: LdapHtmlElement) -> HtmlElement:
    # child texts
    texts = (
        (_get_nth(text), to_html_text(text)) for text in search(conn, l_element.dn, filter_text, LdapHtmlText)
    )
    # child elements
    elements = (
        (_get_nth(l_element), to_html_element(conn, elem)) for elem in search(conn, l_element.dn, filter_element, LdapHtmlElement)
    )
    # sort praticles
    sorted_elements = sorted(itertools.chain(texts, elements), key=itemgetter(0))
    children = [index_elm[1] for index_elm in sorted_elements]

    # attributes
    attrs = {}
    for l_html_attr, html_attr in ELEMENT_ATTR_DICT.items():
        values = getattr(l_element, l_html_attr)
        if len(values) > 0:
            attrs[html_attr] = values[0].decode()

    return HtmlElement(
        l_element.dn, l_element.htmlTagName[0].decode(), attrs, children
    )


def to_html_file(conn: ldap3.Connection, l_html_file: LdapHtmlFile) -> HtmlFile:
    top_l_html_element = next(search(conn, l_html_file.dn, filter_element, LdapHtmlElement))
    top_html_element = to_html_element(conn, top_l_html_element)
    return HtmlFile(l_html_file.o[0], top_html_element)

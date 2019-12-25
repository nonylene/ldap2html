import re
from html.parser import HTMLParser
from typing import List, Tuple, Optional, Container, Dict

from ..html.model import HtmlElement, HtmlNormalElement, HtmlText, HtmlVoidElement
from ..ldap.model import LdapHtmlNormalElement, LdapHtmlText, LdapHtmlParticle, LdapHtmlVoidElement, ELEMENT_ATTR_DICT, LdapBase, LdapHtmlFile


VOID_TAGS = ("area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr")

ELEMENT_DN_PATTERN = re.compile(r'^ou=([\w-]+),')


class Parser(HTMLParser):

    parents: List[HtmlNormalElement] = list()
    top: HtmlNormalElement = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        attr_dict = dict(attrs)
        _id = attr_dict.pop('id', None)

        if tag in VOID_TAGS:
            self.parents[-1].children.append(HtmlVoidElement(_id, tag, attr_dict))
            return

        self.parents.append(HtmlNormalElement(_id, tag, attr_dict, list()))

    def handle_endtag(self, tag: str):
        if tag in VOID_TAGS:
            return

        element = self.parents.pop()
        if self.parents:
            self.parents[-1].children.append(element)
        else:
            self.top = element

    def handle_data(self, data: str):
        if not self.parents:
            # Initial status
            return
        self.parents[-1].children.append(HtmlText(data))


def _to_ldap_html_attrs(attributes: Dict[str, str]) -> Dict[str, List[bytes]]:
    attrs = {}
    for l_html_attr, html_attr in ELEMENT_ATTR_DICT.items():
        value = attributes.get(html_attr, None)
        attrs[l_html_attr] = [value.encode('utf-8')] if value is not None else []
    return attrs


def to_ldap_html_normal_element(
    element: HtmlNormalElement, dn: str, ou: str, nth: Optional[int],
) -> LdapHtmlNormalElement:
    l_nth = [nth] if nth is not None else []
    attrs = _to_ldap_html_attrs(element.attributes)
    l_element = LdapHtmlNormalElement(
        dn, l_nth, [ou], [element.tag_name.encode('utf-8')], **attrs,
    )
    return l_element


def to_ldap_html_void_element(
    element: HtmlVoidElement, dn: str, ou: str, nth: Optional[int],
) -> LdapHtmlVoidElement:
    l_nth = [nth] if nth is not None else []
    attrs = _to_ldap_html_attrs(element.attributes)
    l_element = LdapHtmlVoidElement(
        dn, l_nth, [ou], [element.tag_name.encode('utf-8')], **attrs,
    )
    return l_element


def to_ldap_html_text(
    text: HtmlText, dn: str, cn: str, nth: Optional[int],
) -> LdapHtmlNormalElement:
    l_nth = [nth] if nth is not None else []
    return LdapHtmlText(dn, l_nth, [cn], [text.value.encode('utf-8')])


def _generate_unique_id(used: Container[str], candidate: str) -> str:
    if candidate not in used:
        return candidate

    pattern = re.compile(rf'^{re.escape(candidate)}_(\d+)$')

    max_index = 0
    for _id in used:
        matched = pattern.match(_id)
        if matched:
            max_index = max(max_index, int(matched.group(1)))

    return f"{candidate}_{max_index+1}"


def _generate_good_id(used: List[str], element: HtmlElement) -> str:
    # Preserve dn (best effort)
    if element._id is not None:
        matched = ELEMENT_DN_PATTERN.match(element._id)
        if matched:
            return _generate_unique_id(used, matched.group(1))

    return _generate_unique_id(used, element.tag_name)


def to_ldap_html_particles(element: HtmlNormalElement, dn: str, ou: str, nth: Optional[int]) -> List[LdapHtmlParticle]:
    child_ids = []
    particles = [to_ldap_html_normal_element(element, dn, ou, nth)]

    for idx, child in enumerate(element.children):
        nth = idx if len(element.children) > 1 else None
        if isinstance(child, HtmlNormalElement):
            _id = _generate_good_id(child_ids, child)
            particles.extend(to_ldap_html_particles(child, f"ou={_id},{dn}", _id, nth))

        elif isinstance(child, HtmlVoidElement):
            _id = _generate_good_id(child_ids, child)
            particles.append(to_ldap_html_void_element(child, f"ou={_id},{dn}", _id, nth))

        elif isinstance(child, HtmlText):
            _id = _generate_unique_id(child_ids, 'text')
            particles.append(to_ldap_html_text(child, f"cn={_id},{dn}", _id, nth))

        child_ids.append(_id)

    return particles


def to_ldap_entries(html: str, domain: str, filename: str) -> List[LdapBase]:
    parser = Parser()
    parser.feed(html)

    base_dn = ','.join([f'dc={d}' for d in domain.split('.')])

    file_dn = f'o={filename},{base_dn}'
    ldap_html_file = LdapHtmlFile(file_dn, [filename])

    top_id = _generate_good_id([], parser.top)
    return [ldap_html_file] + to_ldap_html_particles(parser.top, f"ou={top_id},{file_dn}", top_id, None)

import pprint
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
        element = self.parents.pop()
        if self.parents:
            self.parents[-1].children.append(element)
        else:
            self.top = element

    def handle_data(self, data: str):
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
    matched = ELEMENT_DN_PATTERN.match(element._id)
    if matched:
        return _generate_unique_id(used, matched.group(1))
    else:
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


if __name__ == "__main__":
    html = "<!DOCTYPE html><html lang='ja' id='ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><head id='ou=head,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><title id='ou=title,ou=head,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>京都大学 LDIF 同好会</title></head><body id='ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><h1 id='ou=title,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>京都大学 LDIF 同好会</h1><a class='twitter-share-button' href='https://twitter.com/intent/tweet' id='ou=twitter_link,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'></a><h2 id='ou=description_title,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>京都大学 LDIF 同好会とは？</h2><p id='ou=description,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>京都大学 LDIF 同好会とは、 <a href='https://tools.ietf.org/html/rfc2849' id='ou=ldif_link,ou=description,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>LDIF (LDAP Data Interchange Format)</a> が好きな人間が集まる同好会です。</p><h2 id='ou=activities_title,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>活動内容例</h2><ul id='ou=activities_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><li id='ou=activities_write,ou=activities_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><p id='ou=title,ou=activities_write,ou=activities_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>LDIF ファイルを作成する</p><p id='ou=description,ou=activities_write,ou=activities_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>このページの HTML 文書も、 <a href='https://github.com/ku-ldif/ku-ldif.github.io/blob/master/src/index.html.ldif' id='ou=ldif_gh_link,ou=description,ou=activities_write,ou=activities_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>LDIF ファイル</a> から <a href='https://github.com/nonylene/ldap2html' id='ou=ldap2html_link,ou=description,ou=activities_write,ou=activities_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>ldap2html</a> を用いて生成されています！</p></li><li id='ou=activities_dream,ou=activities_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><p id='ou=title,ou=activities_dream,ou=activities_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><a href='/dreams.html' id='ou=href,ou=title,ou=activities_dream,ou=activities_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>LDIF に関する夢</a>を見る</p></li></ul><h2 id='ou=links,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>関連リンク</h2><ul id='ou=links_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><li id='ou=org,ou=links_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><p id='ou=title,ou=org,ou=links_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'><a href='https://github.com/ku-ldif' id='ou=org_link,ou=title,ou=org,ou=links_list,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>GitHub organization</a></p></li></ul><script id='ou=twitter_script,ou=body,ou=html,o=index.html,dc=ku-ldif,dc=github,dc=io'>window.twttr = (function(d, s, id) {  var js, fjs = d.getElementsByTagName(s)[0],    t = window.twttr || {};  if (d.getElementById(id)) return t;  js = d.createElement(s);  js.id = id;  js.src = 'https: // platform.twitter.com/widgets.js';  fjs.parentNode.insertBefore(js, fjs);  t._e = [];  t.ready = function(f) {    t._e.push(f);  };  return t;}(document, 'script', 'twitter-wjs'));</script></body></html>"

    pprint.pprint(to_ldap_entries(html, "example.com", "example.html"))

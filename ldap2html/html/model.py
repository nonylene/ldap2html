from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class HtmlParticle:

    def to_html(self):
        raise NotImplementedError()


@dataclass
class HtmlText:
    value: str

    def to_html(self):
        return self.value


@dataclass
class HtmlElement(HtmlParticle):
    _id: Optional[str]
    tag_name: str
    attributes: Dict[str, str]

    def to_attribute_html(self):
        # attributes
        attributes = self.attributes.copy()
        attributes['id'] = self._id  # _id should be set here
        attrs = ' '.join(f"{k}='{v}'" for k, v in attributes.items())
        return attrs


@dataclass
class HtmlNormalElement(HtmlElement):
    children: List[HtmlParticle]  # ordered

    def to_html(self):
        attrs = self.to_attribute_html()
        # childs
        childs = ''.join(particle.to_html() for particle in self.children)
        return f'<{self.tag_name} {attrs}>{childs}</{self.tag_name}>'


@dataclass
class HtmlVoidElement(HtmlElement):

    def to_html(self):
        attrs = self.to_attribute_html()
        return f'<{self.tag_name} {attrs} />'


@dataclass
class HtmlFile(HtmlParticle):
    filename: str
    child: HtmlElement

    def to_html(self):
        html = self.child.to_html()
        return f'<!DOCTYPE html>{html}'

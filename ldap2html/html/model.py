from dataclasses import dataclass
from typing import List, Dict


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
    _id: str
    tag_name: str
    attributes: Dict[str, str]
    children: List[HtmlParticle]  # ordered

    def to_html(self):
        # attributes
        attributes = self.attributes.copy()
        attributes['id'] = self._id
        attrs = ' '.join(f"{k}='{v}'" for k, v in attributes.items())
        # childs
        childs = ''.join(particle.to_html() for particle in self.children)
        return f'<{self.tag_name} {attrs}>{childs}</{self.tag_name}>'


@dataclass
class HtmlFile(HtmlParticle):
    filename: str
    child: HtmlElement

    def to_html(self):
        html = self.child.to_html()
        return f'<!DOCTYPE html>{html}'

from typing import Optional

from pygls.workspace import Document

from .nodes import XmlSyntaxNode, XmlElement
from .types import DocumentType, NodeType


class XmlDocument(XmlSyntaxNode):
    def __init__(self, document: Document):
        super().__init__()
        self.document: Document = document

    @property
    def node_type(self) -> NodeType:
        return NodeType.DOCUMENT

    @property
    def is_empty(self) -> bool:
        return not self.root

    @property
    def root(self) -> Optional[XmlElement]:
        if len(self.children) == 0:
            return None
        try:
            return next(child for child in self.children if type(child) == XmlElement)
        except StopIteration:
            return None

    @property
    def document_type(self) -> DocumentType:
        try:
            if self.root.name == "tool":
                return DocumentType.TOOL
            if self.root.name == "macros":
                return DocumentType.MACROS
        except BaseException:
            pass
        return DocumentType.UNKNOWN

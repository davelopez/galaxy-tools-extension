"""This module provides a service to determine position context inside an XML document."""

from typing import List, Optional

from pygls.types import Range
from pygls.workspace import Document, Position

from .xml.constants import UNDEFINED_OFFSET, NEW_LINE
from .xml.nodes import XmlSyntaxNode
from .xml.parser import XmlDocumentParser
from .xml.types import NodeType
from .xsd.types import XsdNode, XsdTree


class XmlContext:
    """Represents the context at a given XML document position.

    It provides information about the token under the cursor and
    the XSD node definition associated.
    """

    def __init__(
        self,
        xsd_node: XsdNode,
        node: Optional[XmlSyntaxNode] = None,
        line_text: str = "",
        position: Optional[Position] = None,
        offset: int = UNDEFINED_OFFSET,
    ):
        self._xsd_node: XsdNode = xsd_node
        self._node: Optional[XmlSyntaxNode] = node
        self._line_text: str = line_text
        self._position: Optional[Position] = position
        self._offset: int = offset

    @property
    def token(self) -> Optional[XmlSyntaxNode]:
        """The syntax node at the context position."""
        return self._node

    @property
    def position(self) -> Optional[Position]:
        """The context position inside de Document."""
        return self._position

    @property
    def line_text(self) -> str:
        """The text contents of the document line at the context position."""
        return self._line_text

    @property
    def xsd_element(self) -> XsdNode:
        """The XSD element associated with the token in context."""
        return self._xsd_node

    @property
    def is_empty(self) -> bool:
        """Indicates if the document is empty and no context can be determined."""
        return not self._node

    @property
    def is_tag(self) -> bool:
        """Indicates if the token in context is a tag."""
        return self._node is not None and self._node.node_type == NodeType.ELEMENT

    @property
    def is_attribute_key(self) -> bool:
        """Indicates if the token in context is an attribute key."""
        return self._node is not None and self._node.node_type == NodeType.ATTRIBUTE_KEY

    @property
    def is_attribute_value(self) -> bool:
        """Indicates if the token in context is an attribute value."""
        return self._node is not None and self._node.node_type == NodeType.ATTRIBUTE_VALUE

    @property
    def attribute_name(self) -> Optional[str]:
        """The name of the attribute if the context is an attribute or None."""
        return self._node is not None and self._node.get_attribute_name()

    @property
    def is_content(self) -> bool:
        """Indicates if the token in context is within a content or CDATA block."""
        return self._node is not None and (
            self._node.node_type == NodeType.CONTENT or self._node.node_type == NodeType.CDATA_SECTION
        )

    @property
    def is_closing_tag(self) -> bool:
        """Indicates if the token in context is a closing tag."""
        return self._node is not None and self._node.is_at_closing_tag(self._offset)

    @property
    def stack(self) -> List[str]:
        """The list of XML tag names from the root to the token in context."""
        if not self._node:
            return []
        return self._node.stack


class XmlContextService:
    """This service provides information about the XML context at
    a specific position of the document.
    """

    def __init__(self, xsd_tree: XsdTree):
        self.xsd_tree = xsd_tree

    def get_xml_context(self, document: Document, position: Position) -> XmlContext:
        """Gets the XML context at a given position inside the document.

        Args:
            document (Document): The current document.
            position (Position): The position inside de document.

        Returns:
            XmlContext: The resulting context with the current node
            definition and other information. If the context can not be
            determined, the default context with no information is returned.
        """
        offset = document.offset_at_position(position)

        parser = XmlDocumentParser()
        xml_document = parser.parse(document)
        if xml_document.is_empty:
            return XmlContext(self.xsd_tree.root, node=None)
        node = xml_document.get_node_at(offset)
        xsd_node = self.find_matching_xsd_element(node, self.xsd_tree)
        line_text = document.lines[position.line]
        context = XmlContext(xsd_node, node, line_text, position)
        return context

    def find_matching_xsd_element(self, node: Optional[XmlSyntaxNode], xsd_tree: XsdTree) -> XsdNode:
        """Finds the xsd element in the XSD tree that matches the xml element associated with the given syntax node.
        If there is no matching node, the root (tool) xsd node is always returned.

        Args:
            node (XmlSyntaxNode): The syntax node to match.
            xsd_tree (XsdTree): The XSD tree definition.

        Returns:
            XsdNode: The matching xsd node.
        """
        if node:
            xsd_node = xsd_tree.find_node_by_stack(node.stack)
            if xsd_node:
                return xsd_node
        return xsd_tree.root

    def get_range_from_offsets(self, document: Document, start_offset: int, end_offset: int) -> Range:
        start_line = max(document.source.count(NEW_LINE, 0, start_offset), 0)
        start_character = start_offset - document.source.rfind(NEW_LINE, 0, start_offset)
        end_line = max(document.source.count(NEW_LINE, 0, end_offset), 0)
        end_character = end_offset - document.source.rfind(NEW_LINE, 0, end_offset)
        return Range(
            Position(start_line, start_character),
            Position(end_line, end_character),
        )

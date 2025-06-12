from datetime import date, datetime
from xml.etree.ElementTree import Element


class XMLService:
    def get_str_node(self, node: Element | None) -> str | None:
        if node is None:
            return None
        return node.text or None

    def get_date_node(self, node: Element | None, date_format: str) -> date | None:
        if node is None or node.text is None:
            return None
        return datetime.strptime(node.text, date_format).date()

    def get_float_node(self, node: Element | None) -> float | None:
        if node is None or node.text is None:
            return None
        return float(node.text)

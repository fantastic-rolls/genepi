from textual.widget import Widget


def make_panel_view(title: str, elem: Widget) -> Widget:
    elem.border_title = title
    elem.classes = "border"
    return elem

import plotext as plt


class UI:
    VALID_THEMES = [
        "default",
        "clear",
        "pro",
        "matrix",
        "windows",
        "dark",
        "retro",
        "elegant",
        "mature",
        "dreamland",
        "grandpa",
        "salad",
        "girly",
        "serious",
        "sahara",
        "scream",
    ]

    def __init__(self, max_ui_entries=20, theme="pro") -> None:
        self.max_ui_entries = max_ui_entries
        self._plt = plt

        if theme not in UI.VALID_THEMES:
            self.theme = "pro"
        else:
            self.theme = theme

        self._plt.theme(self.theme)
        """
        example
        {
            "cpu_temp": {
                "label": "CPU temp",
                "data": [20.1, 83.2, 63.2],
            }
        }
        """
        self.displayed_graphs = {}

    def add_source(self, name, label):
        self.displayed_graphs[name] = {"data": [], "label": label}

    def append_data(self, name, data):
        self.displayed_graphs[name]["data"].append(data)

    def draw(self):
        # Map over each currently displayed graph.
        # If graph length exceeds max_ui_entries, then
        # pop the first element
        for curr_item in self.displayed_graphs:
            item = self.displayed_graphs[curr_item]
            (
                item["data"].pop(0)
                if len(item["data"]) + 1 >= self.max_ui_entries
                else None
            )

        self._plt.clear_terminal()
        self._plt.clear_data()

        for item in self.displayed_graphs:
            current_item = self.displayed_graphs[item]
            self._plt.plot(current_item["data"], label=current_item["label"])

        self._plt.show()

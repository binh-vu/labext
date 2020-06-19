from typing import List, Dict, Tuple, Callable, Any, Optional

from IPython.core.display import display

from labext.apps.annotators import PersistentAnnotator, Example, widgets


class ClassificationAnnotator(PersistentAnnotator[str]):
    """For annotating example that belongs to one of N different classes
    """

    def __init__(self, output_file: str, examples: List[Example], class_ids: List[str],
                 classes: Optional[List[str]] = None):
        """
        Parameters
        ----------
        output_file: str
            the journal (output) file that the labeled information is stored
        examples: List[Example]
            list of examples that we need to annotate
        class_ids: List[str]
            list of classes' ids
        classes: Optional[List[str]]
            labels of classes, default to be the classes' ids
        """
        assert all(l is not None and l != "" and l.strip() == l
                   for l in class_ids), "Invalid class id, they should be not null, " \
                                        "not empty and do not contain any head or tail extra spaces"

        super().__init__(output_file, examples)
        classes = classes or class_ids

        # define the UI
        self.el_view = [widgets.HTML(value="<b>Initialize...</b>")]
        self.el_btns = []
        self.el_btns_index = {}
        self.keys = {ci: str(k) for ci, k in enumerate("1234567890qwertyuiopasdfghjklzxcvm")}
        self.reverse_keys = {v: k for k, v in self.keys.items()}

        for ci, c in enumerate(classes):
            if ci in self.keys:
                key = f" ({self.keys[ci]})"
            else:
                key = ""

            btn = widgets.Button(
                description=f"{c}{key}",
                disabled=False,
                button_style='',
                layout=widgets.Layout(width="auto")
            )
            if len(self.el_btns) > 0:
                btn.layout.margin = "0 0 0 8px"
            btn.on_click(self.click)
            self.el_btns.append(btn)
            self.el_btns_index[btn] = ci

        self.el_view.append(widgets.HBox(self.el_btns))
        self.el_view.append(widgets.Output())

        # data
        self.is_view_rendered = False
        self.n_examples = len(examples)
        self.classes = classes
        self.class_ids = class_ids
        self.update_status()

    def render_example(self):
        if self.current_index >= len(self.examples):
            with self.el_view[-1]:
                self.el_view[-1].clear_output()
            for btn in self.el_btns:
                btn.button_style = ''
        else:
            example = self.examples[self.current_index]
            with self.el_view[-1]:
                self.el_view[-1].clear_output()
                example.render()

            if self.has_label(example.id):
                user_choice = self.get_label(example.id)
                for ci, class_id in enumerate(self.class_ids):
                    if class_id == user_choice:
                        self.el_btns[ci].button_style = 'primary'
                    else:
                        self.el_btns[ci].button_style = ''
            else:
                for btn in self.el_btns:
                    btn.button_style = ''

        if not self.is_view_rendered:
            self.is_view_rendered = True
            with self.el_example_container:
                self.el_example_container.clear_output()
                display(*self.el_view)

    def next(self):
        self.current_index += 1
        self.update_status()

    def prev(self):
        self.current_index -= 1
        self.update_status()

    def receive_key(self, key, altKey: bool, ctrlKey: bool, shiftKey: bool, metaKey: bool):
        if key not in self.reverse_keys:
            return

        ci = self.reverse_keys[key]
        class_id = self.class_ids[ci]
        self.update_example_label(class_id)

    def on_clear(self, _btn: widgets.Button) -> None:
        # somehow calling super does not work
        self.current_index = 0
        self.examples = [e for e in self.examples if e.id not in self.labeled_examples]
        self.render_example()
        self.sync_navigator()
        self.update_status()

    def click(self, btn):
        """A button is clicked, we need to figure out the class of that example"""
        ci = self.el_btns_index[btn]
        class_id = self.class_ids[ci]
        self.update_example_label(class_id)

    def update_example_label(self, class_id: str):
        """Toggle label of the current example

        Parameters
        ----------
        class_id: str
            id of the current class. If the current class is this class, we mark this example
            hasn't been labeled (delete previous annotation)
        """
        example_id = self.examples[self.current_index].id

        if self.has_label(example_id) and self.get_label(example_id) == class_id:
            for btn in self.el_btns:
                btn.button_style = ''
            class_id = None
        else:
            for ci, class_id_prime in enumerate(self.class_ids):
                if class_id == class_id_prime:
                    self.el_btns[ci].button_style = 'primary'
                else:
                    self.el_btns[ci].button_style = ''

        self.persist_changes([(example_id, class_id)])
        self.update_status()

    def update_status(self):
        n_discard_examples = self.n_examples - len(self.examples)
        n_labeled = self.no_labeled_examples() - n_discard_examples
        n_examples = len(self.examples)
        self.el_view[0].value = f"<b>Current example</b>: {self.current_index} / {n_examples}. <b>Progress</b>: {round(n_labeled * 100 / max(n_examples, 1), 2)}% ({n_labeled} / {n_examples})"

    def serialize_label(self, label: str) -> str:
        return label

    def deserialize_label(self, ser_label: str) -> str:
        return ser_label
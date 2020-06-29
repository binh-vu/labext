import math
from typing import List, Tuple, Optional
from uuid import uuid4

import ipywidgets.widgets as widgets
from IPython.core.display import display

from labext.apps.annotators.base_annotator import Example
from labext.apps.annotators.persistent_annotator import PersistentAnnotator


class BatchClassificationAnnotator(PersistentAnnotator[str]):
    """An annotator that shows multiple examples per page, each example belongs to one of N different classes.
    """

    def __init__(self, output_file: str, examples: List[Example], class_ids: List[str], classes: Optional[List[str]]=None, batch_size: int=5):
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
        batch_size: int
            number of examples per page.
        """
        assert all(l is not None and l != "" and l.strip() == l
                   for l in class_ids), "Invalid class id, they should be not null, " \
                                        "not empty and do not contain any head or tail extra spaces"

        super().__init__(output_file, examples)
        classes = classes or class_ids

        # setup the UI
        self.no_class_id = str(uuid4())
        assert self.no_class_id not in class_ids

        self.el_default_choice = widgets.Dropdown(
            options=[('disable', self.no_class_id)] + [(c, cid) for c, cid in zip(classes, class_ids)],
            value=self.no_class_id,
            description='Default choice:',
            style={'description_width': 'initial'}
        )
        self.el_default_choice.layout.margin = "0 0 0 8px"
        self.el_default_choice.observe(self.on_default_choice_change, names='value')

        self.el_root_children = (
            widgets.HBox([self.el_prev_btn, self.el_next_btn, self.el_clear_btn, self.el_default_choice, self.el_status_box]),
            self.el_example_container
        )

        self.is_view_rendered = False
        self.el_view = [widgets.HTML(value="<b>Initialize...</b>")]
        self.el_view_outputs = []
        self.el_btns_lst = []

        # bi, ci => ()
        self.keys = {
            (bi, ci): f"{modifier}{c}"
            for bi, c in enumerate("1234567890qwertyuiopasdfghjklzxcvm")
            for ci, modifier in enumerate(["", "ctrl-", "meta-"])
        }
        self.reverse_keys = {
            (c, ctrlKey, metaKey): (bi, ci)
            for bi, c in enumerate("1234567890qwertyuiopasdfghjklzxcvm")
            for ci, (ctrlKey, metaKey) in enumerate([(False, False), (True, False), (False, True)])
        }
        self.el_btns_lst_index = {}

        for bi in range(batch_size):
            btns = []
            for ci, c in enumerate(classes):
                if (bi, ci) in self.keys:
                    key = f" ({self.keys[(bi, ci)]})"
                else:
                    key = ""

                btn = widgets.Button(
                    description=f"{c}{key}",
                    disabled=False,
                    button_style='',
                    layout=widgets.Layout(width="auto")
                )
                if len(btns) > 0:
                    btn.layout.margin = "0 0 0 8px"
                btn.on_click(self.click)
                btns.append(btn)
                self.el_btns_lst_index[btn] = (bi, ci)

            self.el_btns_lst.append(btns)
            self.el_view_outputs.append(widgets.Output())
            row = widgets.HBox(btns + [self.el_view_outputs[-1]])
            self.el_view.append(row)

        # variable to compute the current status
        self.n_examples = len(examples)
        self.classes = classes
        self.class_ids = class_ids
        self.batch_size = batch_size
        self.current_index = 0
        self.default_choice = None if self.el_default_choice.value == self.no_class_id else self.el_default_choice.value
        # use this to mark what examples has been auto-label using default choice, so that we can undo the auto-label op
        self.auto_label_examples: List[Optional[str]] = [None for _ in range(self.batch_size)]
        self.update_status()

    def render_example(self):
        batch_examples = self.examples[self.current_index:self.current_index + self.batch_size]

        # render each example
        for i, e in enumerate(batch_examples):
            with self.el_view_outputs[i]:
                self.el_view_outputs[i].clear_output()
                e.render()

            if self.has_label(e.id):
                user_choice = self.get_label(e.id)
                for ci, class_id in enumerate(self.class_ids):
                    if class_id == user_choice:
                        self.el_btns_lst[i][ci].button_style = 'primary'
                    else:
                        self.el_btns_lst[i][ci].button_style = ''
            else:
                for ci in range(len(self.class_ids)):
                    self.el_btns_lst[i][ci].button_style = ''

        for i in range(len(batch_examples), self.batch_size):
            with self.el_view_outputs[i]:
                self.el_view_outputs[i].clear_output()
            for ci in range(len(self.class_ids)):
                self.el_btns_lst[i][ci].button_style = ''

        if not self.is_view_rendered:
            self.is_view_rendered = True
            with self.el_example_container:
                self.el_example_container.clear_output()
                display(*self.el_view)

    def has_next(self):
        return self.current_index + self.batch_size < len(self.examples)

    def next(self):
        self.current_index += self.batch_size
        self.set_auto_label()
        self.update_status()

    def has_prev(self):
        return self.current_index - self.batch_size >= 0

    def prev(self):
        self.current_index -= self.batch_size
        self.set_auto_label()
        self.update_status()

    def update_status(self):
        n_discard_examples = self.n_examples - len(self.examples)
        n_labeled = self.no_labeled_examples() - n_discard_examples
        n_examples = len(self.examples)
        self.el_view[0].value = f"<b>Current batch</b>: {math.ceil(self.current_index / self.batch_size)} / {math.ceil(n_examples / self.batch_size)}. <b>Progress</b>: {round(n_labeled * 100 / max(n_examples, 1), 2)}% ({n_labeled} / {n_examples})"

    def on_clear(self, _btn: widgets.Button) -> None:
        # somehow calling super does not work
        self.current_index = 0
        self.examples = [e for e in self.examples if e.id not in self.labeled_examples]
        self.render_example()
        self.sync_navigator()
        self.update_status()

    def click(self, btn):
        """A button is clicked, we need to figure out the class of that example"""
        bi, ci = self.el_btns_lst_index[btn]
        if self.current_index + bi >= len(self.examples):
            return

        class_id = self.class_ids[ci]
        self.update_examples([(self.current_index + bi, class_id)], toggle=True)

    def receive_key(self, key, altKey: bool, ctrlKey: bool, shiftKey: bool, metaKey: bool):
        if (key, ctrlKey, metaKey) not in self.reverse_keys:
            return

        bi, ci = self.reverse_keys[(key, ctrlKey, metaKey)]
        if self.current_index + bi >= len(self.examples):
            return

        class_id = self.class_ids[ci]
        self.update_examples([(self.current_index + bi, class_id)], toggle=True)

    def on_default_choice_change(self, change):
        self.default_choice = None if change['new'] == self.no_class_id else change['new']
        batch_examples = self.examples[self.current_index:self.current_index + self.batch_size]
        changes = []
        for i, e in enumerate(batch_examples):
            if self.auto_label_examples[i] == e.id or not self.has_label(e.id):
                changes.append((self.current_index + i, self.default_choice))
                self.auto_label_examples[i] = e.id

        self.update_examples(changes, toggle=False)

    def set_auto_label(self):
        # update default choice change
        if self.default_choice is None:
            # we do not have a default choice, so do not attempt to set it
            return

        batch_examples = self.examples[self.current_index:self.current_index + self.batch_size]
        changes = []
        for i, e in enumerate(batch_examples):
            if self.has_label(e.id):
                self.auto_label_examples[i] = None
            else:
                self.auto_label_examples[i] = e.id
                changes.append((self.current_index + i, self.default_choice))

        for i in range(len(batch_examples), self.batch_size):
            self.auto_label_examples[i] = None

        self.update_examples(changes, toggle=False)

    def update_examples(self, labels: List[Tuple[int, str]], toggle: bool):
        changes = []
        for example_index, class_id in labels:
            example_id = self.examples[example_index].id
            if self.has_label(example_id) and self.get_label(example_id) == class_id and not toggle:
                continue

            bi = example_index - self.current_index
            if self.has_label(example_id) and self.get_label(example_id) == class_id:
                if not toggle:
                    continue

                # toggle
                for ci in range(len(self.class_ids)):
                    self.el_btns_lst[bi][ci].button_style = ''

                changes.append((example_id, None))

            else:
                for ci, class_id_prime in enumerate(self.class_ids):
                    if class_id == class_id_prime:
                        self.el_btns_lst[bi][ci].button_style = 'primary'
                    else:
                        self.el_btns_lst[bi][ci].button_style = ''
                changes.append((example_id, class_id))
        self.persist_changes(changes)
        self.update_status()

    def serialize_label(self, label: str) -> str:
        return label

    def deserialize_label(self, ser_label: str) -> str:
        return ser_label
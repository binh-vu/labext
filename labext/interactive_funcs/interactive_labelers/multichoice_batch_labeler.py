from typing import List, Dict
from IPython.core.display import display
from ipyevents import Event
import ipywidgets.widgets as widgets

from labext.interactive_funcs.interactive_labelers.persistent_interactive_labeler import PersistentInteractiveLabeler
from labext.interactive_funcs.interactive_labelers.interactive_labeler import Example

class BatchMultichoiceClassificationLabeler(PersistentInteractiveLabeler):

    def __init__(self, output_file: str, examples: List[Example], class_ids: List[str], classes: List[str]=None, batch_size: int=5):
        assert len(class_ids) <= 4, "This labeler does not support more than 4 classes"
        assert batch_size <= 9, "This labeler does not support labeling more than 9 examples simultaneously"

        super().__init__(output_file, examples, class_ids)
        self.original_examples = examples
        self.classes = classes or class_ids
        self.batch_size = batch_size
        self.current_index = 0

        # render placeholder to avoid re-rendering
        self.is_view_rendered = False
        self.view = [widgets.HTML(value="<b>Initialize...</b>")]
        self.view_outputs = []
        self.btns_lst = []
        self.update_status()
        for bi in range(self.batch_size):
            btns = []
            for ci, c in enumerate(self.classes):
                if ci == 0:
                    modifier_key = ""
                elif ci == 1:
                    modifier_key = "ctrl-"
                elif ci == 2:
                    modifier_key = "alt-"
                elif ci == 3:
                    modifier_key = "meta-"
                else:
                    raise Exception("Unreachable!")

                btn = widgets.Button(
                    description=f"{c} ({modifier_key}{bi+1})",
                    disabled=False,
                    button_style='',
                )
                if len(btns) > 0:
                    btn.layout.margin = "0 0 0 8px"
                btn.on_click(self.click)
                btns.append(btn)
            self.btns_lst.append(btns)
            self.view_outputs.append(widgets.Output())
            row = widgets.HBox(btns + [self.view_outputs[-1]])
            self.view.append(row)

    def render_example(self, output_area: widgets.Output):
        batch_examples = self.examples[self.current_index:self.current_index + self.batch_size]
        # render each example
        for i, e in enumerate(batch_examples):
            with self.view_outputs[i]:
                self.view_outputs[i].clear_output()
                e.render()

            if self.has_label(e.id):
                user_choice = self.get_label(e.id)
                for ci, class_id in enumerate(self.class_ids):
                    if class_id == user_choice:
                        self.btns_lst[i][ci].button_style = 'primary'
                    else:
                        self.btns_lst[i][ci].button_style = ''
            else:
                for ci in range(len(self.class_ids)):
                    self.btns_lst[i][ci].button_style = ''

        if not self.is_view_rendered:
            self.is_view_rendered = True
            with output_area:
                output_area.clear_output()
                display(*self.view)

    def has_next(self):
        return self.current_index + self.batch_size < len(self.examples)

    def next(self):
        self.current_index += self.batch_size
        self.update_status()

    def has_prev(self):
        return self.current_index - self.batch_size >= 0

    def prev(self):
        self.current_index -= self.batch_size
        self.update_status()

    def update_status(self):
        self.view[0].value = f"<b>Current batch</b>: {self.current_index}. <b>Progress</b>: {round(len(self.labeled_examples) * 100 / len(self.original_examples), 2)}% ({len(self.labeled_examples)} / {len(self.original_examples)})"

    def click(self, btn):
        """A button is clicked, we need to figure out the class of that example"""
        for bi, btns in enumerate(self.btns_lst):
            if self.current_index + bi >= len(self.examples):
                break

            for ci, target_btn in enumerate(btns):
                if target_btn == btn:
                    class_id = self.class_ids[ci]
                    self.label_example(self.current_index + bi, class_id, toggle=True)

    def receive_key(self, key, altKey: bool, ctrlKey: bool, shiftKey: bool, metaKey: bool):
        if not metaKey and not ctrlKey and not altKey:
            class_id = self.class_ids[0]
        elif len(self.classes) > 1 and ctrlKey:
            class_id = self.class_ids[1]
        elif len(self.classes) > 2 and altKey:
            class_id = self.class_ids[2]
        elif len(self.classes) > 3 and metaKey:
            class_id = self.class_ids[3]
        else:
            return

        if key.isdigit():
            bi = int(key) - 1
            if self.current_index + bi >= len(self.examples):
                return
            self.label_example(self.current_index + bi, class_id, toggle=True)

    def label_example(self, example_index: int, class_id: str, toggle: bool = False):
        example_id = self.examples[example_index].id
        if example_id in self.labeled_examples and self.labeled_examples[example_id] == class_id and not toggle:
            return

        bi = example_index - self.current_index
        if self.labeled_examples.get(example_id, None) == class_id:
            if not toggle:
                return

            # toggle
            for ci in range(len(self.class_ids)):
                self.btns_lst[bi][ci].button_style = ''

            self.persist_changes([(example_id, None)])
            self.update_status()
        else:
            for ci, class_id_prime in enumerate(self.class_ids):
                if class_id == class_id_prime:
                    self.btns_lst[bi][ci].button_style = 'primary'
                else:
                    self.btns_lst[bi][ci].button_style = ''
            self.persist_changes([(example_id, class_id)])
            self.update_status()

    def on_clear(self, btn):
        self.examples = [e for e in self.examples if e.id not in self.labeled_examples]
        self.current_index = 0
        self.render_example(self.output_area)

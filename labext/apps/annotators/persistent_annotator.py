import csv
import logging
import os
from typing import List, Dict, Tuple, Optional

from labext.apps.annotators.base_annotator import Annotator, Example
import ipywidgets.widgets as widgets


class PersistentAnnotator(Annotator):
    """An abstract annotator that stores the annotation result to disk.

    To prevent loss, all changes are flush to disk immediately. To make it efficient,
    each operation (delete, upsert) is written to each row. The labeled data is reconstructed
    by replaying the operation logs. Hence, it's important to optimize the logs before
    using the file directly without the annotator.
    """

    logger = logging.getLogger("labext.apps.annotators.persistent_annotator")

    def __init__(self, output_file: str, examples: List[Example], class_ids: List[str]):
        """
        Parameters
        ----------
        output_file: str
            the journal (output) file that the labeled information is stored
        examples: List[Example]
            list of examples that we need to annotate
        class_ids: List[str]
            list of classes that we want to tag each example with. Each example is tagged with
            only one class.
        """
        assert all(l is not None and l != "" and l.strip() == l
                   for l in class_ids), "Invalid class id, they should be not null, " \
                                        "not empty and do not contain any head or tail extra spaces"
        super().__init__()

        # update the UI
        # add clear button to remove annotated examples
        self.el_clear_btn = widgets.Button(
            description='Clear',
            disabled=False,
            button_style='',
            icon='eraser'
        )
        self.el_clear_btn.layout.margin = "0 0 0 8px"
        self.el_clear_btn.on_click(self.on_clear)

        # add the clear  button to the root component
        self.el_root_children = (
            widgets.HBox([self.el_prev_btn, self.el_next_btn, self.el_clear_btn, self.el_status_box]),
            self.el_example_container
        )

        # now setup the data
        # list of examples
        self.examples = examples
        # classes that will be tagged with each example
        self.class_ids = class_ids
        # index of the currrent example
        self.current_index = 0

        # store labeled data: example_id => class_id
        self.labeled_examples: Dict[str, str] = {}
        # output file
        self.output_file = output_file

        if os.path.exists(output_file):
            self.logger.debug("Load output file...")
            with open(output_file, "r") as f:
                reader = csv.reader(f, delimiter='\t')
                n_changes = 0
                del_examples = set()
                set_class_ids = set(class_ids)

                for example_id, class_id in reader:
                    if class_id == "":
                        class_id = None
                    else:
                        assert class_id in set_class_ids

                    if example_id in self.labeled_examples:
                        n_changes += 1

                    self.labeled_examples[example_id] = class_id

                    if class_id is None:
                        del_examples.add(example_id)
                    elif example_id in del_examples:
                        del_examples.remove(example_id)

                for example_id in del_examples:
                    assert self.labeled_examples[example_id] is None
                    del self.labeled_examples[example_id]

            if len(self.labeled_examples) == 0 or n_changes / len(self.labeled_examples) > 0.2:
                # so many duplication, optimize the log
                self.logger.debug("Optimizing existing output file as it contains many duplications...")
                self.optimize_journal_file()
            self.logger.debug("Finish loading output file...")

    def persist_changes(self, changes: List[Tuple[str, Optional[str]]]) -> None:
        """Persist the changes to the disk.

        Parameters
        ----------
        changes: List[Tuple[str, Optional[str]]]
            List of changes, each change is a pair of (`example_id`, and `class_id`).
            To delete a label of an example, set `class_id` to None
        """
        with open(self.output_file, "a") as f:
            writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            for example_id, class_id in changes:
                if class_id is None:
                    del self.labeled_examples[example_id]
                else:
                    self.labeled_examples[example_id] = class_id
                writer.writerow([example_id, class_id])

    def optimize_journal_file(self):
        """Optimize the journal (output) file.
        """
        with open(self.output_file + ".tmp", "w") as f:
            writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            for example_id, class_id in self.labeled_examples.items():
                writer.writerow([example_id, class_id])

        os.rename(self.output_file, self.output_file + ".backup")
        os.rename(self.output_file + ".tmp", self.output_file)
        os.remove(self.output_file + ".backup")

    def get_label(self, example_id: str) -> str:
        """Get label of this example

        Parameters
        ----------
        example_id: str
            id of the wanted example
        Returns
        -------
        str
            the label (i.e., `class_id`) associated with the example
        """
        return self.labeled_examples[example_id]

    def has_label(self, example_id: str) -> bool:
        """Telling if the example has been labeled

        Parameters
        ----------
        example_id: str
            id of the wanted example
        Returns
        -------
        bool
            `true` if the example has been labeled
        """
        return example_id in self.labeled_examples

    def on_clear(self, _btn: widgets.Button) -> None:
        """Clear annotated examples

        Parameters
        ----------
        _btn: widgets.Button
            the clear button
        """
        self.current_index = 0
        self.examples = [e for e in self.examples if e.id not in self.labeled_examples]
        self.render_example()

    def next(self):
        self.current_index += 1

    def prev(self):
        self.current_index -= 1

    def has_next(self):
        return self.current_index + 1 < len(self.examples)

    def has_prev(self):
        return self.current_index > 0

    def render_example(self):
        with self.el_example_container:
            self.el_example_container.clear_output()
            self.examples[self.current_index].render()

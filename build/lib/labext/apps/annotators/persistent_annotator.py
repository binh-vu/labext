import csv
import logging
import os
from abc import abstractmethod
from typing import List, Dict, Tuple, Optional, Generic, TypeVar

from labext.apps.annotators.base_annotator import Annotator, Example
import ipywidgets.widgets as widgets


Label = TypeVar("Label")


class PersistentAnnotator(Annotator, Generic[Label]):
    """An abstract annotator that stores the annotation result to disk.

    To prevent loss, all changes are flush to disk immediately. To make it efficient,
    each operation (delete, upsert) is written to each row. The labeled data is reconstructed
    by replaying the operation logs. Hence, it's important to optimize the logs before
    using the file directly without the annotator.
    """

    logger = logging.getLogger("labext.apps.annotators.persistent_annotator")

    def __init__(self, output_file: str, examples: List[Example]):
        """
        Parameters
        ----------
        output_file: str
            the journal (output) file that the labeled information is stored
        examples: List[Example]
            list of examples that we need to annotate
        """
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
        # index of the currrent example
        self.current_index = 0

        # store labeled data: example_id => label.
        self.labeled_examples: Dict[str, Label] = {}
        # output file
        self._output_file = output_file

        if os.path.exists(output_file):
            self.logger.debug("Load output file...")
            with open(output_file, "r") as f:
                reader = csv.reader(f, delimiter='\t')
                n_changes = 0
                del_examples = set()

                for example_id, label in reader:
                    if label == "":
                        label = None
                    else:
                        label = self.deserialize_label(label)

                    if example_id in self.labeled_examples:
                        n_changes += 1

                    self.labeled_examples[example_id] = label

                    if label is None:
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

    def persist_changes(self, changes: List[Tuple[str, Optional[Label]]]) -> None:
        """Persist the changes to the disk.

        Parameters
        ----------
        changes: List[Tuple[str, Optional[str]]]
            List of changes, each change is a pair of (`example_id`, and `label`).
            To delete a label of an example, set `label` to None
        """
        with open(self._output_file, "a") as f:
            writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            for example_id, label in changes:
                if label is None:
                    del self.labeled_examples[example_id]
                else:
                    self.labeled_examples[example_id] = label
                writer.writerow([example_id, self.serialize_label(label)])

    def optimize_journal_file(self):
        """Optimize the journal (output) file.
        """
        with open(self._output_file + ".tmp", "w") as f:
            writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            for example_id, label in self.labeled_examples.items():
                writer.writerow([example_id, self.serialize_label(label)])

        os.rename(self._output_file, self._output_file + ".backup")
        os.rename(self._output_file + ".tmp", self._output_file)
        os.remove(self._output_file + ".backup")

    def no_labeled_examples(self) -> int:
        """Get the number of examples that has been annotated

        Returns
        -------
        int
        """
        return len(self.labeled_examples)

    def get_label(self, example_id: str) -> Label:
        """Get label of this example

        Parameters
        ----------
        example_id: str
            id of the wanted example
        Returns
        -------
        str
            the label (i.e., `label`) associated with the example
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

    @abstractmethod
    def serialize_label(self, label: Label) -> str:
        """Serialize the label to string in order to save it to disk. The function must not return an empty string as it
        is reserved for null value

        Parameters
        ----------
        label: Label

        Returns
        -------
        str
            the serialized string, must not be empty
        """
        pass

    @abstractmethod
    def deserialize_label(self, ser_label: str) -> Label:
        """Deserialize the label

        Parameters
        ----------
        ser_label: str

        Returns
        -------
        Label
        """
        pass

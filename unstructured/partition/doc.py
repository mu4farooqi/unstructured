import os
import tempfile
from typing import IO, List, Optional

from unstructured.documents.elements import Element
from unstructured.partition.common import convert_office_doc, exactly_one
from unstructured.partition.docx import partition_docx


def partition_doc(filename: Optional[str] = None, file: Optional[IO] = None) -> List[Element]:
    """Partitions Microsoft Word Documents in .doc format into its document elements.

    Parameters
    ----------
    filename
        A string defining the target filename path.
    file
        A file-like object using "rb" mode --> open(filename, "rb").
    """
    # Verify that only one of the arguments was provided
    exactly_one(filename=filename, file=file)

    if filename is not None:
        _, filename_no_path = os.path.split(os.path.abspath(filename))
        base_filename, _ = os.path.splitext(filename_no_path)
    elif file is not None:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(file.read())
        tmp.close()
        filename = tmp.name
        _, filename_no_path = os.path.split(os.path.abspath(tmp.name))
    else:
        raise ValueError("Exactly one of filename and file must be specified.")

    if not os.path.exists(filename):
        raise ValueError(f"The file {filename} does not exist.")

    base_filename, _ = os.path.splitext(filename_no_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        convert_office_doc(filename, tmpdir, target_format="docx")
        docx_filename = os.path.join(tmpdir, f"{base_filename}.docx")
        elements = partition_docx(filename=docx_filename, metadata_filename=filename)

    return elements

import logging
from pathlib import Path

import mkdocs.plugins

logger = logging.getLogger("mkdocs")

THIS_DIR = Path(__file__).parent
ROOT_DIR = THIS_DIR.parent
DOCS_DIR = ROOT_DIR / "docs"


@mkdocs.plugins.event_priority(-50)
def on_pre_build(config) -> None:
    add_docs("CHANGELOG.md")
    add_docs("UPGRADING.md")


def add_docs(doc_file: str) -> None:
    root_doc_file = ROOT_DIR / doc_file
    docs_doc_file = DOCS_DIR / doc_file

    old_doc_file = docs_doc_file.read_text() if docs_doc_file.is_file() else None

    if old_doc_file != (new_doc_file := root_doc_file.read_text()):
        docs_doc_file.write_text(new_doc_file)
        logger.info("%s copied to %s", root_doc_file, docs_doc_file)

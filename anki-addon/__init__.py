"""Pealim Verb Cards: build Anki cards for Hebrew verbs from pealim.com.

Anki loads this file at startup;
it only adds the toolbar link.
The rest is in flow.py.
"""

from aqt import gui_hooks
from aqt.toolbar import Toolbar

from .flow import add_verb


def add_toolbar_link(links: list[str], toolbar: Toolbar) -> None:
    links.append(
        toolbar.create_link(
            "pealim",
            "Pealim",
            add_verb,
            tip="Add a Hebrew verb from pealim.com",
            id="pealim",
        )
    )


gui_hooks.top_toolbar_did_init_links.append(add_toolbar_link)

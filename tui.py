#!/usr/bin/env python3
"""
The Wellness Hub — Site Management TUI
"""

import subprocess
import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, DataTable, TabbedContent,
    TabPane, Label, ListView, ListItem, MarkdownViewer,
)
from textual.containers import Horizontal, Vertical, ScrollableContainer, Container
from textual import on
from textual.reactive import reactive
from rich.text import Text

SITE_ROOT = Path(__file__).parent

TIMETABLE = {
    "Monday": [
        ("6:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("7:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("9:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("10:30 AM", "Small Group PT", "Strength"),
        ("6:00 PM", "Small Group PT", "Strength"),
        ("7:00 PM", "LTL (Ladies That Lift)", "Strength"),
    ],
    "Tuesday": [
        ("6:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("9:30 AM", "Small Group PT", "Strength"),
        ("5:30 PM", "LTL (Ladies That Lift)", "Strength"),
        ("6:30 PM", "Small Group PT", "Strength"),
    ],
    "Wednesday": [
        ("6:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("7:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("9:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("10:30 AM", "Small Group PT", "Strength"),
        ("6:30 PM", "Small Group PT", "Strength"),
        ("7:00 PM", "LTL (Ladies That Lift)", "Strength"),
    ],
    "Thursday": [
        ("6:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("9:30 AM", "Small Group PT", "Strength"),
        ("5:30 PM", "LTL (Ladies That Lift)", "Strength"),
        ("6:30 PM", "Small Group PT", "Strength"),
    ],
    "Friday": [
        ("6:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("7:30 AM", "LTL (Ladies That Lift)", "Strength"),
        ("9:30 AM", "LTL + Small Group PT", "Strength"),
    ],
    "Saturday": [
        ("7:30 AM", "LTL + Small Group PT", "Strength"),
        ("9:00 AM", "Mobility", "Mobility"),
        ("10:30 AM", "Pilates", "Pilates"),
    ],
    "Sunday": [
        ("9:30 AM", "Pilates", "Pilates"),
        ("10:30 AM", "Pilates", "Pilates"),
    ],
}

PAGES = [
    ("Home", "team.html"),
    ("Our Story", "main.js"),
    ("Classes", "howto.html"),
    ("Timetable", "style.css"),
    ("Team", "timetable.html"),
    ("How-To Guides", "privacy.html"),
    ("My Bookings", "contact.html"),
    ("Contact", "index.html"),
    ("Privacy", "terms.html"),
    ("Terms", "why.html"),
]

DASHBOARD_MD = """\
# The Wellness Hub — Dublin

**A dedicated wellness studio for women navigating post-menopause.**

---

## Studio Details

| | |
|---|---|
| **Location** | Donaghmede, Dublin 13 (D13TX67) |
| **Phone** | 086 210 6867 |
| **Email** | kelley@thewellnesshub.ie |
| **Instagram** | @kelleythewellnesshub |
| **Booking** | LegitFit platform |

---

## Three Pillars

1. **Strength** — Small-group LTL (Ladies That Lift) sessions; max 12 per class
2. **Pilates** — Weekend Pilates with Sara Connor
3. **Nutrition** — 1:1 consultations (booked separately)

---

## Site Pages (10)

Home · Our Story · Classes · Timetable · Team · How-To Guides · My Bookings · Contact · Privacy · Terms
"""

CLASSES_MD = """\
# Classes & Pricing

---

## LTL — Ladies That Lift
*Strength · Mon–Fri*

Structured small-group strength training built specifically for post-menopausal women.
Sessions focus on safe form, progressive load, and genuine coaching in a calm environment.
Maximum 12 members per session.

---

## Small Group PT
*Strength · Mon–Thu + Fri*

Personalised strength work in a small group setting. Similar structure to LTL with
a more flexible programme design week to week.

---

## Pilates
*Pilates · Sat–Sun*

Weekend Pilates with **Sara Connor**. Focuses on core stability, breath, and controlled
movement — an ideal complement to weekday strength sessions.

---

## Mobility
*Saturday mornings*

Dedicated mobility and recovery work. Complements the strength programme.

---

## Hyrox (Seasonal)
*Tue + Thu — twice per year*

8-week Hyrox prep block. Community-led training for the Hyrox race format.

---

## Nutrition 1:1
*By appointment*

Private nutrition consultations. Booked separately — enquire directly for availability.

---

# Pricing

| Tier | Price | Notes |
|---|---|---|
| **Drop-in** | €12 / class | Any class on timetable (excl. Hyrox) |
| **Membership** | €80 / month | 2 classes per week |
| **Hyrox Block** | Seasonal | 8-week block, twice per year |
| **Nutrition 1:1** | Enquire | Separate from class pricing |
"""

TEAM_MD = """\
# Team

---

## Kelley Connor
**Owner · Founder · Menopause Coach**

Kelley runs The Wellness Hub in Donaghmede, Dublin — a supportive studio for women
who want strength and calm in the post-menopause years. Sessions stay small so you
get real coaching, not a crowded class vibe.

**Credentials & Highlights:**
- Creator of **LTL** (Ladies That Lift) — a structured strength block with clear progression
- Small-group strength sessions built around safe form and confidence
- Menopause coaching specialist
- Instagram: @kelleythewellnesshub

---

## Sara Connor
**Pilates Instructor**

Sara leads weekend Pilates sessions at the studio — focused on core stability,
breath work, and controlled movement as a complement to the weekday strength programme.

---

*Small team. Big support.*
"""


def class_style(class_type: str) -> str:
    styles = {
        "Strength": "bold green",
        "Pilates": "bold magenta",
        "Mobility": "bold cyan",
    }
    return styles.get(class_type, "white")


class DashboardPane(ScrollableContainer):
    def compose(self) -> ComposeResult:
        yield MarkdownViewer(DASHBOARD_MD, show_table_of_contents=False)


class TimetablePane(Container):
    def compose(self) -> ComposeResult:
        yield Static(
            "[bold]Weekly Class Schedule[/bold]  "
            "  [green]■[/green] Strength  [magenta]■[/magenta] Pilates  [cyan]■[/cyan] Mobility",
            id="tt-legend",
        )
        yield DataTable(id="timetable-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Day", "Time", "Class", "Type")
        table.cursor_type = "row"

        for day, sessions in TIMETABLE.items():
            first = True
            for time, name, cls_type in sessions:
                day_label = day if first else ""
                first = False
                style = class_style(cls_type)
                table.add_row(
                    Text(day_label, style="bold yellow" if day_label else ""),
                    Text(time, style="dim"),
                    Text(name, style=style),
                    Text(cls_type, style=style),
                )


class ClassesPane(ScrollableContainer):
    def compose(self) -> ComposeResult:
        yield MarkdownViewer(CLASSES_MD, show_table_of_contents=False)


class TeamPane(ScrollableContainer):
    def compose(self) -> ComposeResult:
        yield MarkdownViewer(TEAM_MD, show_table_of_contents=False)


class SiteFilesPane(Container):
    selected_file: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="file-list-panel"):
                yield Static("[bold]Site Pages[/bold]", id="file-panel-header")
                yield ListView(
                    *[ListItem(Label(f"  {name}  ({fname})"), id=f"page-{i}")
                      for i, (name, fname) in enumerate(PAGES)],
                    id="file-list",
                )
            with Vertical(id="file-content-panel"):
                yield Static("[bold]File Details[/bold]", id="file-content-header")
                yield Static(
                    "Select a page from the list to view details.",
                    id="file-content-body",
                )

    def on_mount(self) -> None:
        self.query_one("#file-list", ListView).focus()

    @on(ListView.Selected)
    def page_selected(self, event: ListView.Selected) -> None:
        idx = int(event.item.id.split("-")[1])
        page_name, filename = PAGES[idx]
        filepath = SITE_ROOT / filename
        size_kb = filepath.stat().st_size / 1024 if filepath.exists() else 0
        status = "✓ exists" if filepath.exists() else "✗ missing"

        content = (
            f"[bold yellow]{page_name}[/bold yellow]\n\n"
            f"[dim]File:[/dim]    {filename}\n"
            f"[dim]Path:[/dim]    {filepath}\n"
            f"[dim]Size:[/dim]    {size_kb:.1f} KB\n"
            f"[dim]Status:[/dim]  {status}\n\n"
            f"[dim]─────────────────────────────────────────[/dim]\n\n"
        )

        if filepath.exists():
            try:
                raw = filepath.read_text(errors="replace")
                import re
                title = re.search(r"<title>([^<]+)</title>", raw)
                desc = re.search(r'<meta name="description" content="([^"]+)"', raw)
                h1 = re.search(r"<h1[^>]*>([^<]+)", raw)
                if title:
                    content += f"[bold]Title:[/bold] {title.group(1)}\n"
                if desc:
                    content += f"[bold]Description:[/bold] {desc.group(1)}\n"
                if h1:
                    content += f"[bold]H1:[/bold] {h1.group(1).strip()}\n"
                links = re.findall(r'href="([^"]+)"', raw)
                internal = [l for l in links if not l.startswith("http") and ".html" in l]
                external = [l for l in links if l.startswith("http")]
                content += f"\n[dim]Internal links:[/dim] {len(set(internal))}\n"
                content += f"[dim]External links:[/dim] {len(set(external))}\n"
            except Exception as e:
                content += f"[red]Error reading file: {e}[/red]"

        self.query_one("#file-content-body", Static).update(content)


class WellnessHubTUI(App):
    CSS = """
    Screen {
        background: #1a1612;
    }

    Header {
        background: #2a2018;
        color: #c9a96e;
        text-style: bold;
    }

    Footer {
        background: #2a2018;
        color: #6b5f54;
    }

    TabbedContent {
        height: 1fr;
    }

    TabPane {
        padding: 0;
    }

    #tt-legend {
        padding: 1 2;
        background: #2a2018;
        color: #c9a96e;
    }

    DataTable {
        height: 1fr;
        background: #1a1612;
    }

    DataTable > .datatable--header {
        background: #2a2018;
        color: #c9a96e;
        text-style: bold;
    }

    DataTable > .datatable--cursor {
        background: #3a2e20;
    }

    MarkdownViewer {
        background: #1a1612;
        color: #f8f4ee;
        padding: 1 3;
    }

    #file-list-panel {
        width: 38;
        border-right: solid #3a2e20;
    }

    #file-panel-header {
        padding: 1 2;
        background: #2a2018;
        color: #c9a96e;
        text-style: bold;
    }

    #file-list {
        height: 1fr;
        background: #1a1612;
    }

    ListView > ListItem {
        color: #f8f4ee;
        padding: 0 1;
    }

    ListView > ListItem.--highlight {
        background: #3a2e20;
        color: #c9a96e;
    }

    #file-content-panel {
        width: 1fr;
    }

    #file-content-header {
        padding: 1 2;
        background: #2a2018;
        color: #c9a96e;
        text-style: bold;
    }

    #file-content-body {
        padding: 1 2;
        color: #f8f4ee;
        height: 1fr;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "switch_tab('dashboard')", "Dashboard"),
        ("2", "switch_tab('timetable')", "Timetable"),
        ("3", "switch_tab('classes')", "Classes"),
        ("4", "switch_tab('team')", "Team"),
        ("5", "switch_tab('pages')", "Pages"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                yield DashboardPane()
            with TabPane("Timetable", id="timetable"):
                yield TimetablePane()
            with TabPane("Classes", id="classes"):
                yield ClassesPane()
            with TabPane("Team", id="team"):
                yield TeamPane()
            with TabPane("Site Pages", id="pages"):
                yield SiteFilesPane()
        yield Footer()

    def action_switch_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    @on(TabbedContent.TabActivated)
    def tab_activated(self, event: TabbedContent.TabActivated) -> None:
        if event.tab.id == "tab-pages":
            self.set_timer(0.05, lambda: self.query_one("#file-list", ListView).focus())


if __name__ == "__main__":
    app = WellnessHubTUI()
    app.title = "The Wellness Hub"
    app.sub_title = "Dublin · Strength • Pilates • Nutrition"
    app.run()

"""Spinx configuration file for the ViperBoxInterface documentation.

The documentation is generated from the README.md file in the root of the repository.
The README.md file is copied to the Sphinx source directory and processed to generate
the documentation. The following transformations are applied to the README.md file:

1. Replace named emojis with unicode emojis.
2. Replace markdown alerts with admonitions.
3. Replace relative links to `example/` files with absolute links to GitHub.
4. Fix anchors with named emojis.
5. Split the README.md file into individual sections based on second-level headers.
6. Extract the table of contents links from the processed README.
7. Replace links in each section to point to the correct section.
8. Decrease the header levels by one in each section.
9. Rename the first section to `introduction.md` and update its header.
10. Write an index file for the documentation.

This code is tightly coupled with the structure of the README.md file and the
table of contents generated by the doctoc tool.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import textwrap
from pathlib import Path

package_path = Path("../..").resolve()
sys.path.insert(0, str(package_path))
PYTHON_PATH = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = f"{package_path}:{PYTHON_PATH}"

docs_path = Path("..").resolve()
sys.path.insert(1, str(docs_path))

from viperboxinterface import __version__  # noqa: E402

project = "ViperBoxInterface"
copyright = "2024, Stijn Balk"  # noqa: A001
author = "Stijn Balk"

version = __version__
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinx_autodoc_typehints",
]


autosectionlabel_maxdepth = 5
myst_heading_anchors = 0
templates_path = ["_templates"]
source_suffix = [".rst", ".md"]
master_doc = "index"
language = "en"
pygments_style = "sphinx"
html_theme = "furo"
html_static_path = ["_static"]
htmlhelp_basename = "ViperBoxInterfacedoc"
default_role = "autolink"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
html_logo = "https://github.com/sbalk/ViperBoxInterface/blob/main/imgs/viperboxinterface.png?raw=true"


def replace_named_emojis(input_file: Path, output_file: Path) -> None:
    """Replace named emojis in a file with unicode emojis."""
    import emoji

    with input_file.open("r") as infile:
        content = infile.read()
    content_with_emojis = emoji.emojize(content, language="alias")

    with output_file.open("w") as outfile:
        outfile.write(content_with_emojis)


def _change_alerts_to_admonitions(input_text: str) -> str:
    # Splitting the text into lines
    lines = input_text.split("\n")

    # Placeholder for the edited text
    edited_text = []

    # Mapping of markdown markers to their new format
    mapping = {
        "IMPORTANT": "important",
        "NOTE": "note",
        "TIP": "tip",
        "WARNING": "caution",
    }

    # Variable to keep track of the current block type
    current_block_type = None

    for line in lines:
        # Check if the line starts with any of the markers
        if any(line.strip().startswith(f"> [!{marker}]") for marker in mapping):
            # Find the marker and set the current block type
            current_block_type = next(
                marker for marker in mapping if f"> [!{marker}]" in line
            )
            # Start of a new block
            edited_text.append("```{" + mapping[current_block_type] + "}")
        elif current_block_type and line.strip() == ">":
            # Empty line within the block, skip it
            continue
        elif current_block_type and not line.strip().startswith(">"):
            # End of the current block
            edited_text.append("```")
            edited_text.append(line)  # Add the current line as it is
            current_block_type = None  # Reset the block type
        elif current_block_type:
            # Inside the block, so remove '>' and add the line
            edited_text.append(line.lstrip("> ").rstrip())
        else:
            # Outside any block, add the line as it is
            edited_text.append(line)

    # Join the edited lines back into a single string
    return "\n".join(edited_text)


def change_alerts_to_admonitions(input_file: Path, output_file: Path) -> None:
    """Change markdown alerts to admonitions.

    For example, changes
    > [!NOTE]
    > This is a note.
    to
    ```{note}
    This is a note.
    ```
    """
    with input_file.open("r") as infile:
        content = infile.read()
    new_content = _change_alerts_to_admonitions(content)

    with output_file.open("w") as outfile:
        outfile.write(new_content)


def replace_image_links(input_file: Path, output_file: Path) -> None:
    """Replace relative links to `./imgs/` files with absolute links to GitHub."""
    with input_file.open("r") as infile:
        content = infile.read()
    new_content = (
        content.replace(
            "(./imgs/",
            "(https://github.com/sbalk/ViperBoxInterface/blob/main/imgs/",
        )
        .replace(".png)", ".png?raw=true)")
        .replace(".gif)", ".gif?raw=true)")
    )
    with output_file.open("w") as outfile:
        outfile.write(new_content)


def fix_anchors_with_named_emojis(input_file: Path, output_file: Path) -> None:
    """Fix anchors with named emojis.

    WARNING: this currently hardcodes the emojis to remove.
    """
    to_remove = [
        "brain",
        "books",
        "desktop_computer",
        "gear",
        "question",
        "robot",
        "hammer_and_wrench",
        "memo",
    ]
    with input_file.open("r") as infile:
        content = infile.read()
    new_content = content
    for emoji_name in to_remove:
        new_content = new_content.replace(f"#{emoji_name}-", "#")
    with output_file.open("w") as outfile:
        outfile.write(new_content)


def normalize_slug(slug: str) -> str:
    """Normalize a slug."""
    return "#" + slug[1:].lstrip("-").rstrip("-")


def split_markdown_by_headers(
    readme_path: Path,
    out_folder: Path,
    links: dict[str, str],
    level: int = 2,
    to_skip: tuple[str, ...] = ("Table of Contents",),
) -> list[str]:
    """Split a markdown file into individual files based on headers."""
    with readme_path.open(encoding="utf-8") as file:
        content = file.read()

    # Regex to find second-level headers
    n = "#" * level
    headers = re.finditer(rf"\n({n} .+?)(?=\n{n} |\Z)", content, re.DOTALL)

    # Split content based on headers
    split_contents: list[str] = []
    header_contents: list[str] = []
    start = 0
    previous_header = ""
    for header in headers:
        header_title = header.group(1).strip("# ").strip()
        header_contents.append(header_title.split("\n", 1)[0])
        end = header.start()
        if not any(s in previous_header for s in to_skip):
            split_contents.append(content[start:end].strip())
        start = end
        previous_header = header_title

    # Add the last section
    split_contents.append(content[start:].strip())

    # Create individual files for each section
    toctree_entries = []
    for i, (section, header_content) in enumerate(
        zip(split_contents, header_contents),
    ):
        name = (
            normalize_slug(links[header_content]).lstrip("#")
            if header_content in links
            else f"section_{i}"
        )
        fname = out_folder / f"{name}.md"
        toctree_entries.append(name)
        with fname.open("w", encoding="utf-8") as file:
            file.write(section)

    return toctree_entries


def replace_header(file_path: Path, new_header: str) -> None:
    """Replace the first-level header in a markdown file."""
    with file_path.open("r", encoding="utf-8") as file:
        content = file.read()

    # Find the first-level header (indicated by '# ')
    # We use a regular expression to match the first occurrence of '# '
    # and any following characters until a newline
    content = re.sub(
        r"^# .+?\n",
        f"# {new_header}\n",
        content,
        count=1,
        flags=re.MULTILINE,
    )

    with file_path.open("w", encoding="utf-8") as file:
        file.write(content)


def extract_toc_links(md_file_path: Path) -> dict[str, str]:
    """Extracts the table of contents with title to link mapping from the given README content.

    Parameters
    ----------
    md_file_path
        Markdown file path.

    Returns
    -------
    A dictionary where keys are section titles and values are the corresponding links.

    """
    with md_file_path.open("r") as infile:
        readme_content = infile.read()
    toc_start = "<!-- START doctoc generated TOC please keep comment here to allow auto update -->"
    toc_end = "<!-- END doctoc generated TOC please keep comment here to allow auto update -->"

    # Extract the TOC section
    toc_section = re.search(f"{toc_start}(.*?){toc_end}", readme_content, re.DOTALL)
    if not toc_section:
        msg = "Table of Contents section not found."
        raise RuntimeError(msg)

    toc_content = toc_section.group(1)

    # Regular expression to match the markdown link syntax
    link_regex = re.compile(r"- \[([^]]+)\]\(([^)]+)\)")

    # Extracting links
    return {
        match.group(1).strip(): match.group(2)
        for match in link_regex.finditer(toc_content)
    }


def extract_headers_from_markdown(md_file_path: Path) -> list[tuple[int, str]]:
    """Extracts all headers from a markdown file.

    Parameters
    ----------
    md_file_path
        Path to the markdown file.

    Returns
    -------
    A list of tuples containing the level of the header and the header text.

    """
    with md_file_path.open("r") as infile:
        content = infile.read()

    # Regex to match markdown headers (e.g., ## Header)
    header_regex = re.compile(r"^(#+)\s+(.+)$", re.MULTILINE)

    # Extract headers
    return [
        (len(match.group(1)), match.group(2).strip())
        for match in header_regex.finditer(content)
    ]


def replace_links_in_markdown(
    md_file_path: Path,
    headers_mapping: dict[str, list[tuple[int, str]]],
    links: dict[str, str],
) -> None:
    """Replaces markdown links with updated links that point to the correct file and header anchor.

    Parameters
    ----------
    md_file_path
        Path to the markdown file to process.
    headers_mapping
        A dictionary where keys are markdown file names and values are lists of headers.
    links
        A dictionary of original header texts mapped to their slug (anchor) in the original README.

    """
    with md_file_path.open("r") as infile:
        content = infile.read()

    # Replace links based on headers_mapping and links dictionary
    for file_name, headers in headers_mapping.items():
        for _header_level, header_text in headers:
            # Find the original slug for this header text from the links dictionary
            original_slug = links.get(header_text, "")
            if original_slug:
                # Remove the '#' from the slug and update the link in the content
                new_slug = normalize_slug(original_slug)
                original_slug = original_slug.lstrip("#")
                content = content.replace(
                    f"(#{original_slug})",
                    f"({file_name}{new_slug})",
                )

    # Write updated content back to file
    with md_file_path.open("w") as outfile:
        outfile.write(content)


def decrease_header_levels(md_file_path: Path) -> None:
    """Decreases the header levels by one in a Markdown file, without going below level 1.

    Parameters
    ----------
    md_file_path
        Path to the Markdown file.

    """
    with md_file_path.open("r", encoding="utf-8") as file:
        content = file.read()

    # Function to decrease the header level
    def lower_header_level(match: re.Match) -> str:
        header_level = len(match.group(1))
        new_header_level = "#" * max(1, header_level - 1)  # Ensure at least one '#'
        return f"{new_header_level} {match.group(2)}"

    # Regular expression for Markdown headers
    header_regex = re.compile(r"^(#+)\s+(.+)$", re.MULTILINE)

    # Replace headers with decreased levels
    new_content = header_regex.sub(lower_header_level, content)

    # Write the updated content back to the file
    with md_file_path.open("w", encoding="utf-8") as file:
        file.write(new_content)


def write_index_file(docs_path: Path, toctree_entries: list[str]) -> None:
    """Write an index file for the documentation."""
    index_path = docs_path / "source" / "index.md"
    # Skip section_0.md as it is renamed to introduction.md
    pages = "\n".join(f"{entry}" for entry in toctree_entries[1:])
    # Constructing the content using textwrap.dedent for better readability
    content = textwrap.dedent(
        """
        ```{{include}} introduction.md
        ```

        ```{{toctree}}
        :hidden: true
        :maxdepth: 2
        :glob:

        introduction
        {pages}
        reference/index
        ```
    """,
    ).format(pages=pages)

    # Write the content to the file
    with index_path.open("w", encoding="utf-8") as index_file:
        index_file.write(content)


def process_readme_for_sphinx_docs(readme_path: Path, docs_path: Path) -> None:
    """Process the README.md file for Sphinx documentation generation.

    Parameters
    ----------
    readme_path
        Path to the original README.md file.
    docs_path
        Path to the Sphinx documentation source directory.

    """
    # Step 1: Copy README.md to the Sphinx source directory and apply transformations
    output_file = docs_path / "source" / "README.md"
    replace_named_emojis(readme_path, output_file)
    change_alerts_to_admonitions(output_file, output_file)
    replace_image_links(output_file, output_file)
    fix_anchors_with_named_emojis(output_file, output_file)

    # Step 2: Extract the table of contents links from the processed README
    links = extract_toc_links(output_file)

    # Step 3: Split the README into individual sections for Sphinx
    src_folder = docs_path / "source"
    for md_file in src_folder.glob("sections_*.md"):
        md_file.unlink()
    toctree_entries = split_markdown_by_headers(output_file, src_folder, links)
    output_file.unlink()  # Remove the original README file from Sphinx source
    write_index_file(docs_path, toctree_entries)

    # Step 4: Extract headers from each section for link replacement
    headers_in_files = {}
    for md_file in src_folder.glob("*.md"):
        headers = extract_headers_from_markdown(md_file)
        decrease_header_levels(md_file)
        headers_in_files[md_file.name] = headers

    # Rename the first section to 'introduction.md' and update its header
    shutil.move(src_folder / "section_0.md", src_folder / "introduction.md")  # type: ignore[arg-type]
    replace_header(src_folder / "introduction.md", new_header="🌟 Introduction")

    # Step 5: Replace links in each markdown file to point to the correct section
    for md_file in (*src_folder.glob("*.md"), src_folder / "introduction.md"):
        replace_links_in_markdown(md_file, headers_in_files, links)


readme_path = package_path / "README.md"
process_readme_for_sphinx_docs(readme_path, docs_path)

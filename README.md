# Pynaptics

Pynaptics is a collection of applications and tools I have developed alongside
my primary work to address the practical needs that arise around it. Most of
these projects began as ways to automate repetitive tasks, organize information,
validate data and files, or make specialized workflows easier to manage.

They are not intended as general-purpose products; each one reflects a specific
problem or working process. However, they are documented and shared here in the
hope that others facing similar needs may find them useful, adapt them to their
own workflows, or use them as a starting point for related projects.

The collection is organized into two categories. 

**Apps** are small, focused
applications-often built around a command-line interface, but not limited to
one-with a defined workflow and a more complete software structure. They are
designed with clear architectural boundaries, validation, automated tests, and
maintainability in mind. 

**Tools** address narrower, self-contained tasks that
do not require the same level of architectural detail. Some could be implemented
as a single script, but they still favor a minimal separation of concerns and a
structure that keeps the code understandable, testable, and reusable.

## Apps

### [Dendrotype](https://github.com/delozath/dendrotype)
[dendrotype]

Dendrotype is a local web editor for Pandera YAML schemas. It provides a visual
interface for reviewing and editing inferred schemas, including column types,
validation checks, reusable templates, metadata, and global schema settings.
The current version is a Django-based, single-user application under active
development; an earlier GTK desktop prototype is preserved separately.

- Status: Usable | Active development

### [Nomnema](https://github.com/delozath/nomnema)
[nomnema]: https://github.com/delozath/nomnema

Nomnema is an experimental desktop-assisted tool for organizing downloaded
academic PDFs into a BibLaTeX-backed literature collection. It extracts a DOI,
retrieves and enriches citation metadata, lets the user review the generated
BibTeX entry, updates an existing bibliography, files the PDF, and creates a
Markdown companion note with the paper's metadata and abstract.

- Status: Usable | Work in progress

## Tools

Utilities and smaller projects will be listed here as they are added.

### [Project name][project-name]

_Short project description._

- Status: _Project status_


[dendrotype]: DENDROTYPE_GITHUB_URL
[nomnema]: NOMNEMA_GITHUB_URL
[project-name]: PROJECT_GITHUB_URL

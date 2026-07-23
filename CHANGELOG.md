# Changelog

All notable changes to Postcanvas are documented here.

## 1.0.1

### Compatibility and release automation

- Added tested support for Python 3.14 while retaining Python 3.10, 3.11, 3.12, and 3.13.
- Added Python-version classifiers for every supported stable interpreter.
- Moved linting, documentation validation, distribution builds, and wheel smoke tests to Python 3.14.
- Kept the release gate across the complete Python 3.10–3.14 matrix.
- Added one-time post-release branch cleanup so the repository retains only `main`.

## 1.0.0

### Documentation and examples

- Rebuilt the project README as a visual product overview.
- Added a complete documentation index and guided learning paths.
- Added dedicated guides for typography, rich text, images, shapes, tables, charts, carousels, templates, validation, profiles, cloud output, assisted selection, architecture, API reference, and migration.
- Added a visual gallery with committed SVG showcase assets.
- Added complete executable examples for editorial graphics, dashboards, stories, carousels, templates, rich text, validation, platform packs, and cloud output.
- Added a documentation workflow that checks local links, assets, required guides, version consistency, example syntax, and an actual rendered preview.

### Stability

- Declared the documented rendering, model, template, validation, rich-text, profile, selector, and output APIs stable for the 1.x series.
- Breaking public API changes now require a new major version.

## 0.3.2

- Added rich-text span composition.
- Added optional dictionary hyphenation and first-line indentation.
- Added the variant selector protocol and prompt-assisted selector adapter.

## 0.3.1

- Added advanced responsive layout nodes, repeaters, inheritance, platform exclusion zones, accessibility checks, automatic focal points, and expanded tests.

## 0.3.0

- Added responsive text fitting, templates, validation, profiles, and release CI.

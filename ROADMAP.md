# Project Roadmap

This document outlines the planned features and improvements for the `tiny_cli` project. The roadmap is subject to change as the project evolves.

---

## **Planned Features**

### Version 0.0.1
- Add support for customizable padding inside message boxes.
- Implement a feature to align text (left, center, right) within the message box.
- Add a CLI command to generate message boxes directly from the terminal.

### Version 0.0.2
- Override command name and command help via decorator arguments.
- Improve error handling and logging for invalid inputs.
- Add style at application level
  - max columns length
  - min columns length


### Version 0.0.3
- Handle command "tree".
- Add long help message, used in specific command help, via decorator.
- Improve the docstring handling to extract brief help and long help.

---

## **Completed Features**
- [x] Initial release with support for creating message boxes.
- [x] Automatic text wrapping based on specified width.
- [x] Support for multiple border styles (`SINGLE_ROUNDED`, `SINGLE_RECTANGLE`, etc.).
- [x] Improved string handling and error handling for edge cases.

---
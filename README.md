# FreeCAD engine summary for CADAI

This repository vendors the official [FreeCAD](https://github.com/FreeCAD/FreeCAD) sources under `freecad/` so that CADAI can drive the CAD kernel in a fully offline, reproducible way. The upstream project is licensed under LGPL-2.0-or-later (see `freecad/LICENSE`).

## Layout highlights
- `freecad/CMakeLists.txt`, `freecad/CMakePresets.json`: root build scripts used to configure all targets with CMake/Ninja across platforms
- `freecad/src/Base`: cross-cutting infrastructure (messaging, parameter system, math helpers, resource loading) shared by the whole application
- `freecad/src/App`: document model, feature graph, transaction management, Python binding glue, and module bootstrap code
- `freecad/src/Gui`: Qt-based user interface (3D viewer, task panels, property editor, selection manager) plus icon resources
- `freecad/src/Main`: entry points that build the GUI executable (`FreeCAD`) and the headless console driver (`FreeCADCmd`)
- `freecad/src/Mod`: workbench plug-ins such as `Part`, `PartDesign`, `Sketcher`, `Mesh`, `Fem`, `TechDraw`, `Assembly`, each combining C++ core code, Python tools, and UI resources
- `freecad/src/Ext/freecad`: bundled Python modules that expose higher-level helpers (e.g. sketcher/part utilities) to macros and external clients
- `freecad/src/Doc`: Sphinx documentation sources and templates shipped with the upstream project
- `freecad/src/Tools` and `freecad/tools/`: utility scripts for code generation, binding builds, XML formatting, linting, profiling, and packaging support
- `freecad/tests`: CTest suites plus Python regression tests that exercise the application and modules
- `freecad/package`: distro packaging specs (Fedora, Ubuntu, rattler-build) used when distributing binaries
- `freecad/build`: default CMake build tree (debug/release) produced by preset workflows; safe to clean/regenerate

## Runtime deliverables
- `FreeCAD` (GUI): launched via `src/Main/MainGui.cpp`, starts Qt, loads modules listed in `Mod/`, and can host interactive workbenches
- `FreeCADCmd` (CLI): built from `src/Main/MainCmd.cpp`, initialises `App::Application` without GUI and executes Python macros or script files; this is what CADAI uses for automation
- Python packages: `src/Ext/freecad` becomes importable inside the embedded interpreter so CLI scripts can reuse upstream utilities alongside module-specific `Init.py` files

## Python and automation surface
- The headless driver embeds CPython via `Base::Interpreter`, exposing the full FreeCAD API (`App`, `Gui`, workbench modules) to scripts
- Each module publishes typed document objects and helper functions under `Mod/<Workbench>`, usually split into `App/` (core C++) and `Gui/` implementations with matching `Init.py`
- CADAI’s `app/tools/freecad_box.py` renders macros, points `FreeCADCmd` at a temporary script, and optionally saves the generated `.FCStd` file; set `FREECAD_CMD` or pass `command=...` to direct the tool at a locally built executable

## Build and development workflow
- Primary build system is CMake; presets (`CMakePresets.json`) define Ninja-based configurations for Linux, macOS, and Windows as well as Release/Debug variants
- `pixi.toml` describes a conda-forge environment with all required dependencies (OCCT, Coin3D, Qt6, SMESH, etc.) and defines convenience tasks: `pixi run configure`, `pixi run build`, `pixi run install`, `pixi run test`
- `tools/build`, `tools/lint`, and `freecad/tools/` scripts automate tasks like binding regeneration, XML formatting, and code style checks
- External libraries that are not fetched via package managers live under `src/3rdParty` (OndselSolver, OCCT helpers, Coin3D patches, etc.)

## Testing guidance
- Module-level tests reside in `freecad/tests/src` (C++) and `freecad/tests/lib` (Python); run them with `pixi run test` or `ctest --test-dir build/<config>` after configuration
- Many workbenches ship dedicated Python test suites (e.g. `Mod/Part/TestPartApp.py`, `Mod/Part/TestPartGui.py`) that can be executed through `FreeCADCmd -c` or within the GUI test runner

## Supporting material
- Community and governance documents: `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `PRIVACY_POLICY.md`
- Packaging and release helpers: `package/`, `build/`, `cMake/` helper modules, and Git submodules initialised via `pixi run initialize`

## Licensing
FreeCAD is available under LGPL-2.0-or-later; check `freecad/LICENSE` for the full text. Some bundled subcomponents ship under permissive licenses noted in their respective directories.

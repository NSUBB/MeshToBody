# MeshToBody FreeCAD Macro

This repository contains the `MeshToBody.py` FreeCAD macro, which converts a selected mesh object into a refined, simple solid and integrates it into a PartDesign Body. The macro is designed to streamline the process of converting mesh objects into solid bodies for further modeling and editing in FreeCAD.

## Features

- Converts a selected mesh into a solid shape.
- Refines the solid to remove unnecessary edges.
- Creates a simple copy of the refined solid.
- Integrates the simple solid into a new PartDesign Body.
- Automatically cleans up intermediate objects after validation.
- Provides user-friendly error messages and progress notifications.

## Requirements

- **FreeCAD**: Ensure you have FreeCAD installed on your system. Version 1.0.1+
- **PySide**: The macro uses PySide for GUI elements, which is included with FreeCAD.

## Installation

1. Download the `MeshToBody.py` file. Rename it with the FCmacro file extension.
2. Place the file in your FreeCAD macros directory. You can find or set the macros directory in FreeCAD under `Edit > Preferences > General > Macro`.
3. Restart FreeCAD if it is already running.

## Usage

1. Open your FreeCAD project and ensure the document is active.
2. Select a mesh object in the 3D view or from the model tree.
3. Run the macro:
   - Open the `Macro` menu in FreeCAD.
   - Select `Macros...`, choose `MeshToBody.py`, and click `Execute`.

### Notes:
- The macro will validate the selection to ensure it is a mesh object.
- If no object is selected or the selected object is not a mesh, the macro will display an error message and terminate.
- The macro will display a "Processing... Please wait." message during execution.

## Output

- A new PartDesign Body containing the converted solid will be created.
- The original mesh and intermediate objects will be removed if the conversion is successful.
- If the conversion fails, the original mesh will be retained.

## Error Handling

- If no object is selected, the macro will prompt the user to select a mesh and terminate.
- If the selected object is not a mesh, the macro will display an error message and terminate.
- If the refined solid is invalid, the macro will retain the original mesh and notify the user.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the macro.

## Disclaimer

This macro is provided "as is" without any warranty. Use it at your own risk.

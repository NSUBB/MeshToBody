# MeshToBody FreeCAD Macro
![MeshToBody](https://github.com/user-attachments/assets/5ead9567-3c8c-40a1-a8f5-066e9259917e)

This repository contains the `MeshToBody.py` FreeCAD macro, which converts a selected mesh object into a refined, simple solid and integrates it into a **PartDesign Body**. The macro ensures the mesh is valid before conversion, allowing users to manually repair it if needed.

## Features

- Evaluates the selected mesh before conversion using FreeCAD’s `Mesh_EvaluateSolid`.
- Provides a **single popup** with three options:
  - ✅ **Yes, Proceed Conversion** → Converts the mesh into a solid.
  - 🛠 **No, Open Repair Mesh** → Runs `Mesh_Evaluation` for manual fixes.
  - ❌ **Cancel Conversion** → Stops execution.
- Converts a selected mesh into a solid shape using `makeShapeFromMesh()`.
- Refines the solid to remove unnecessary edges.
- Creates a simple copy of the refined solid.
- Integrates the simple solid into a new **PartDesign Body**.
- Automatically cleans up intermediate objects after validation.
- Provides user-friendly error messages and progress notifications.
- Supports **undo transactions** for safe modifications.

![image](https://github.com/user-attachments/assets/48df98a9-d1bf-479a-b0e8-8c37be4edf65)

## Requirements

- **FreeCAD** → Version **1.0.1+**
- **PySide** → Required for GUI elements (included with FreeCAD)

## Installation

1. Download the `MeshToBody.py` file and rename it with the `.FCMacro` extension.
2. Place the file in your FreeCAD macros directory:
   - Windows: `C:\Users\<YourUsername>\AppData\Roaming\FreeCAD\Macro\`
   - Linux/macOS: `~/.FreeCAD/Macro/`
3. Restart FreeCAD if it is already running.

## Usage

1. Open your FreeCAD project and ensure the document is active.
2. Select a **mesh object** in the 3D view or from the model tree.
3. Run the macro:
   - Open the **Macro** menu in FreeCAD.
   - Select **Macros...**, choose `MeshToBody.py`, and click **Execute**.

### Mesh Evaluation Process
- The macro first runs **Mesh_EvaluateSolid** to check if the mesh is a valid solid.
- A **popup** appears with three options:
  - ✅ **Yes, Proceed Conversion** → Converts the mesh into a solid.
  - 🛠 **No, Open Repair Mesh** → Runs `Mesh_Evaluation` for manual fixes.
  - ❌ **Cancel Conversion** → Stops execution.
- If conversion proceeds, the macro creates a **PartDesign Body** with a base feature of the refined simple solid.

## Output

- A new **PartDesign Body** containing the converted solid will be created.
- The original mesh and intermediate objects will be removed if the conversion is successful.
- If the conversion fails, the original mesh will be retained.

## Error Handling

- If **no object is selected**, the macro will prompt the user to select a mesh and terminate.
- If the **selected object is not a mesh**, the macro will display an error message and terminate.
- If the **mesh is not a valid solid**, the macro will prompt the user to repair it before proceeding.
- If the **refined solid is invalid**, the macro will retain the original mesh and notify the user.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Contributing

Contributions are welcome! Feel free to submit **issues or pull requests** to improve the macro.

## Disclaimer

This macro is provided **"as is"** without any warranty. Use it at your own risk.

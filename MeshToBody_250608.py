import FreeCAD
import FreeCADGui
import Mesh
import Part
import PartDesign
from PySide import QtGui, QtCore

# --- Helper function to safely close the progress dialog ---
def close_progress_dialog(dialog):
    if dialog and dialog.isVisible():
        dialog.cancel()

# --- Function to trigger Mesh_EvaluateSolid and ask user for confirmation ---
def evaluate_mesh(selected_mesh):
    """Runs Mesh_EvaluateSolid via GUI command and asks the user for confirmation."""
    FreeCADGui.Selection.clearSelection()
    FreeCADGui.Selection.addSelection(selected_mesh)
    FreeCADGui.runCommand('Mesh_EvaluateSolid', 0)

    # **Create a custom dialog for vertical button layout**
    dialog = QtGui.QDialog()
    dialog.setWindowTitle("Mesh Evaluation Result")
    dialog.setLayout(QtGui.QVBoxLayout())  # Use vertical layout

    # **Add label text**
    label = QtGui.QLabel(f"Is the Mesh '{selected_mesh.Name}' a valid solid?")
    dialog.layout().addWidget(label)

    # **Create buttons**
    yes_button = QtGui.QPushButton("✅ Yes, Proceed Conversion")
    repair_button = QtGui.QPushButton("🛠 No, Open Repair Mesh")
    cancel_button = QtGui.QPushButton("❌ Cancel Conversion")

    # **Set button width**
    for button in [yes_button, repair_button, cancel_button]:
        button.setMinimumWidth(250)  # Wider buttons for readability
        button.setMinimumHeight(40)  # Taller buttons for better interaction
        dialog.layout().addWidget(button)  # Add buttons to vertical layout

    # **Connect buttons to dialog result**
    yes_button.clicked.connect(lambda: dialog.done(1))
    repair_button.clicked.connect(lambda: dialog.done(2))
    cancel_button.clicked.connect(lambda: dialog.done(3))

    # **Execute dialog and get result**
    result = dialog.exec_()

    if result == 1:
        return "proceed"
    elif result == 2:
        return "repair"
    else:
        return "cancel"

# --- Main macro function ---
def run_mesh_to_solid_macro():
    doc = FreeCAD.ActiveDocument
    doc.openTransaction("Mesh to Solid Conversion")

    progress_dialog = None
    initial_solid_created = False

    try:
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            QtGui.QMessageBox.warning(None, "Mesh to Solid", "Please select a Mesh and try again.")
            doc.abortTransaction()
            return

        selected_mesh = selection[0]
        if not hasattr(selected_mesh, 'Mesh') or not isinstance(selected_mesh.Mesh, Mesh.Mesh):
            QtGui.QMessageBox.warning(None, "Mesh to Solid", f"Selected object '{selected_mesh.Name}' is not a Mesh.")
            doc.abortTransaction()
            return

        # **Run Mesh_EvaluateSolid and ask user for confirmation**
        user_choice = evaluate_mesh(selected_mesh)

        if user_choice == "repair":
            FreeCADGui.runCommand('Mesh_Evaluation', 0)  # Open full mesh evaluation for manual repair
            doc.abortTransaction()
            return  # Stop execution so the user can fix the mesh

        elif user_choice == "cancel":
            doc.abortTransaction()
            return  # Stop execution entirely

        # **Proceed with conversion if user confirmed**
        progress_dialog = QtGui.QProgressDialog(
            "Processing...", None, 0, 0, FreeCADGui.getMainWindow()
        )
        progress_dialog.setWindowFlags(progress_dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        progress_dialog.setLabelText("Converting mesh to solid... Please wait.")
        progress_dialog.show()
        QtGui.QApplication.processEvents()

        base_name = selected_mesh.Name

        # Convert Mesh to Shape
        shape_obj = doc.addObject('Part::Feature', base_name + "_shape")
        shape = Part.Shape()
        shape.makeShapeFromMesh(selected_mesh.Mesh.Topology, 0.1, False)
        shape_obj.Shape = shape
        shape_obj.purgeTouched()

        # Convert to Solid
        solid_obj = doc.addObject("Part::Feature", base_name + "_solid")
        solid_obj.Shape = Part.Solid(Part.Shell(shape_obj.Shape.Faces))

        # Refine Shape
        refined_obj = doc.addObject("Part::Refine", base_name + "_solid_refined")
        refined_obj.Source = solid_obj
        solid_obj.Visibility = False

        doc.recompute()

        if refined_obj.Shape and refined_obj.Shape.isValid():
            simple_copy_obj = doc.addObject("Part::Feature", base_name + "_solid_simple")
            simple_copy_obj.Shape = refined_obj.Shape

            body_obj = doc.addObject("PartDesign::Body", base_name + "_Body")
            body_obj.BaseFeature = simple_copy_obj
            simple_copy_obj.Visibility = False
            initial_solid_created = True

        else:
            raise ValueError("Refined solid was invalid, so no simple copy or PartDesign Body was created.")

    except Exception as e:
        close_progress_dialog(progress_dialog)
        doc.abortTransaction()
        QtGui.QMessageBox.critical(None, "Mesh to Solid - Error", f"An error occurred:\n\n{e}")
        FreeCAD.Console.PrintError(f"Macro error: {e}\n")
        return

    finally:
        # Cleanup Intermediate Objects
        if 'shape_obj' in locals() and doc.getObject(shape_obj.Name):
            doc.removeObject(shape_obj.Name)
        if 'solid_obj' in locals() and doc.getObject(solid_obj.Name):
            doc.removeObject(solid_obj.Name)
        if 'refined_obj' in locals() and doc.getObject(refined_obj.Name):
            doc.removeObject(refined_obj.Name)

        if initial_solid_created and doc.getObject(selected_mesh.Name):
            doc.removeObject(selected_mesh.Name)
        else:
            FreeCAD.Console.PrintMessage("Conversion failed or was incomplete. Original mesh retained.\n")

    doc.commitTransaction()
    doc.recompute()

    if initial_solid_created:
        close_progress_dialog(progress_dialog)
        QtGui.QMessageBox.information(None, "Mesh to Solid", f"Mesh '{base_name}' successfully converted.")

# --- Call the main function ---
run_mesh_to_solid_macro()

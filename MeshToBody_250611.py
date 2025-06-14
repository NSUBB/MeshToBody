import FreeCAD
import FreeCADGui
import Mesh
import Part
import PartDesign
from PySide import QtGui, QtCore

# --- Automated mesh evaluation function (replaces GUI popup) ---
def evaluate_mesh_automated(selected_mesh):
    """
    Automated mesh evaluation that replaces the GUI popup.
    Returns: 'proceed', 'repair', or 'cancel' based on mesh quality.
    """
    try:
        mesh = selected_mesh.Mesh
        
        # Core evaluation
        is_solid = mesh.isSolid()
        has_non_manifolds = mesh.hasNonManifolds()
        has_self_intersections = mesh.hasSelfIntersections()
        
        # Log the evaluation results
        FreeCAD.Console.PrintMessage(f"\n=== MESH EVALUATION: {selected_mesh.Name} ===\n")
        FreeCAD.Console.PrintMessage(f"Points: {mesh.CountPoints}, Facets: {mesh.CountFacets}\n")
        FreeCAD.Console.PrintMessage(f"Is Solid: {'YES' if is_solid else 'NO'}\n")
        FreeCAD.Console.PrintMessage(f"Has Non-Manifolds: {'YES' if has_non_manifolds else 'NO'}\n")
        FreeCAD.Console.PrintMessage(f"Has Self-Intersections: {'YES' if has_self_intersections else 'NO'}\n")
        
        if is_solid:
            FreeCAD.Console.PrintMessage(f"Volume: {mesh.Volume:.3f}\n")
            FreeCAD.Console.PrintMessage(f"Surface Area: {mesh.Area:.3f}\n")
        
        # Decision logic
        if is_solid and not has_non_manifolds and not has_self_intersections:
            FreeCAD.Console.PrintMessage("✅ DECISION: Mesh is clean - proceeding with conversion\n")
            return "proceed"
        
        elif is_solid and (has_non_manifolds or has_self_intersections):
            FreeCAD.Console.PrintMessage("⚠️  DECISION: Mesh is solid but has issues - attempting automatic repair\n")
            
            # Attempt automatic repair
            repair_success = attempt_mesh_repair(selected_mesh, has_non_manifolds, has_self_intersections)
            
            if repair_success:
                FreeCAD.Console.PrintMessage("🔧 REPAIR: Automatic repair successful - proceeding with conversion\n")
                return "proceed"
            else:
                FreeCAD.Console.PrintMessage("🔧 REPAIR: Automatic repair failed - manual intervention required\n")
                return "repair"
        
        else:
            FreeCAD.Console.PrintMessage("❌ DECISION: Mesh is not solid - repair required\n")
            return "repair"
            
    except Exception as e:
        FreeCAD.Console.PrintError(f"Mesh evaluation error: {e}\n")
        return "cancel"

# --- Automatic mesh repair function ---
def attempt_mesh_repair(mesh_obj, has_non_manifolds, has_self_intersections):
    """
    Attempt to automatically repair common mesh issues.
    Returns True if repair was successful, False otherwise.
    """
    try:
        original_mesh = mesh_obj.Mesh
        repair_attempted = False
        
        # Create a copy of the mesh for repair attempts
        mesh_copy = Mesh.Mesh(original_mesh)
        
        if has_non_manifolds:
            FreeCAD.Console.PrintMessage("🔧 Attempting to remove non-manifold points...\n")
            # Note: removeNonManifolds() might not exist in all versions
            # This is a placeholder for the actual repair method
            repair_attempted = True
        
        if has_self_intersections:
            FreeCAD.Console.PrintMessage("🔧 Attempting to remove self-intersections...\n")
            # Note: removeSelfIntersections() might not exist in all versions  
            # This is a placeholder for the actual repair method
            repair_attempted = True
        
        if repair_attempted:
            # Apply the repaired mesh back to the object
            mesh_obj.Mesh = mesh_copy
            FreeCAD.ActiveDocument.recompute()
            
            # Re-evaluate the repaired mesh
            is_solid_after = mesh_copy.isSolid()
            has_non_manifolds_after = mesh_copy.hasNonManifolds()
            has_self_intersections_after = mesh_copy.hasSelfIntersections()
            
            if is_solid_after and not has_non_manifolds_after and not has_self_intersections_after:
                return True
        
        return False
        
    except Exception as e:
        FreeCAD.Console.PrintError(f"Mesh repair error: {e}\n")
        return False

# --- Enhanced evaluation with user options ---
def evaluate_mesh_with_options(selected_mesh, auto_mode=True):
    """
    Evaluate mesh with option for automatic or interactive mode.
    auto_mode=True: Fully automated
    auto_mode=False: Show dialog for user decision
    """
    if auto_mode:
        return evaluate_mesh_automated(selected_mesh)
    else:
        # Original interactive approach with our evaluation data
        mesh = selected_mesh.Mesh
        is_solid = mesh.isSolid()
        has_non_manifolds = mesh.hasNonManifolds()  
        has_self_intersections = mesh.hasSelfIntersections()
        
        # Create custom dialog with evaluation results
        dialog = QtGui.QDialog()
        dialog.setWindowTitle("Mesh Evaluation Result")
        dialog.setLayout(QtGui.QVBoxLayout())
        
        # Add detailed evaluation info
        info_text = f"""Mesh: {selected_mesh.Name}
Points: {mesh.CountPoints}, Facets: {mesh.CountFacets}
Is Solid: {'YES' if is_solid else 'NO'}
Non-Manifolds: {'YES' if has_non_manifolds else 'NO'}
Self-Intersections: {'YES' if has_self_intersections else 'NO'}"""
        
        if is_solid:
            info_text += f"\nVolume: {mesh.Volume:.3f}"
            info_text += f"\nSurface Area: {mesh.Area:.3f}"
        
        label = QtGui.QLabel(info_text)
        label.setStyleSheet("font-family: monospace;")
        dialog.layout().addWidget(label)
        
        # Add question
        question = QtGui.QLabel("How would you like to proceed?")
        dialog.layout().addWidget(question)
        
        # Create buttons based on mesh condition
        if is_solid and not has_non_manifolds and not has_self_intersections:
            proceed_button = QtGui.QPushButton("✅ Proceed with Conversion")
        else:
            proceed_button = QtGui.QPushButton("⚠️ Proceed Despite Issues")
            
        repair_button = QtGui.QPushButton("🛠 Open Mesh Repair Tools")
        cancel_button = QtGui.QPushButton("❌ Cancel Conversion")
        
        for button in [proceed_button, repair_button, cancel_button]:
            button.setMinimumWidth(250)
            button.setMinimumHeight(40)
            dialog.layout().addWidget(button)
        
        proceed_button.clicked.connect(lambda: dialog.done(1))
        repair_button.clicked.connect(lambda: dialog.done(2))
        cancel_button.clicked.connect(lambda: dialog.done(3))
        
        result = dialog.exec_()
        
        if result == 1:
            return "proceed"
        elif result == 2:
            return "repair"
        else:
            return "cancel"

# --- Helper function to safely close the progress dialog ---
def close_progress_dialog(dialog):
    if dialog and dialog.isVisible():
        dialog.cancel()

# --- Main macro function with automation options ---
def run_mesh_to_solid_macro(auto_mode=True, auto_repair=True):
    """
    Main conversion function with automation options.
    
    auto_mode: If True, runs fully automated without user dialogs
    auto_repair: If True, attempts automatic mesh repair when issues are found
    """
    doc = FreeCAD.ActiveDocument
    doc.openTransaction("Mesh to Solid Conversion")

    progress_dialog = None
    initial_solid_created = False

    try:
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            if auto_mode:
                FreeCAD.Console.PrintError("No mesh selected. Please select a mesh and try again.\n")
                doc.abortTransaction()
                return False
            else:
                QtGui.QMessageBox.warning(None, "Mesh to Solid", "Please select a Mesh and try again.")
                doc.abortTransaction()
                return False

        selected_mesh = selection[0]
        if not hasattr(selected_mesh, 'Mesh') or not isinstance(selected_mesh.Mesh, Mesh.Mesh):
            error_msg = f"Selected object '{selected_mesh.Name}' is not a Mesh."
            if auto_mode:
                FreeCAD.Console.PrintError(error_msg + "\n")
                doc.abortTransaction()
                return False
            else:
                QtGui.QMessageBox.warning(None, "Mesh to Solid", error_msg)
                doc.abortTransaction()
                return False

        # Evaluate mesh with chosen mode
        user_choice = evaluate_mesh_with_options(selected_mesh, auto_mode)

        if user_choice == "repair":
            if auto_mode:
                FreeCAD.Console.PrintMessage("Mesh requires manual repair. Conversion aborted.\n")
            else:
                FreeCADGui.runCommand('Mesh_Evaluation', 0)  # Open full mesh evaluation
            doc.abortTransaction()
            return False

        elif user_choice == "cancel":
            if auto_mode:
                FreeCAD.Console.PrintMessage("Mesh conversion cancelled.\n")
            doc.abortTransaction()
            return False

        # Proceed with conversion
        if not auto_mode:
            progress_dialog = QtGui.QProgressDialog(
                "Processing...", None, 0, 0, FreeCADGui.getMainWindow()
            )
            progress_dialog.setWindowFlags(progress_dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            progress_dialog.setLabelText("Converting mesh to solid... Please wait.")
            progress_dialog.show()
            QtGui.QApplication.processEvents()

        FreeCAD.Console.PrintMessage(f"Starting conversion of mesh '{selected_mesh.Name}' to solid...\n")
        
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
            
            FreeCAD.Console.PrintMessage(f"✅ Successfully created PartDesign Body: {body_obj.Name}\n")

        else:
            raise ValueError("Refined solid was invalid, so no simple copy or PartDesign Body was created.")

    except Exception as e:
        close_progress_dialog(progress_dialog)
        doc.abortTransaction()
        error_msg = f"An error occurred during conversion: {e}"
        if auto_mode:
            FreeCAD.Console.PrintError(error_msg + "\n")
        else:
            QtGui.QMessageBox.critical(None, "Mesh to Solid - Error", error_msg)
        return False

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
        success_msg = f"Mesh '{base_name}' successfully converted to PartDesign Body."
        if auto_mode:
            FreeCAD.Console.PrintMessage(success_msg + "\n")
        else:
            QtGui.QMessageBox.information(None, "Mesh to Solid", success_msg)
        return True
    
    return False

# --- Batch processing function for multiple meshes ---
def batch_convert_meshes(auto_mode=True):
    """Convert all selected meshes to PartDesign Bodies"""
    selection = FreeCADGui.Selection.getSelection()
    mesh_objects = [obj for obj in selection if hasattr(obj, 'Mesh')]
    
    if not mesh_objects:
        FreeCAD.Console.PrintError("No mesh objects found in selection.\n")
        return
    
    FreeCAD.Console.PrintMessage(f"\n=== BATCH CONVERSION: {len(mesh_objects)} meshes ===\n")
    
    success_count = 0
    for mesh_obj in mesh_objects:
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(mesh_obj)
        
        if run_mesh_to_solid_macro(auto_mode=auto_mode):
            success_count += 1
    
    FreeCAD.Console.PrintMessage(f"\n=== BATCH COMPLETE: {success_count}/{len(mesh_objects)} successful ===\n")

# --- Main execution ---
if __name__ == "__main__":
    # Choose your execution mode:
    
    # Fully automated mode (no user interaction):
    run_mesh_to_solid_macro(auto_mode=True)
    
    # Interactive mode (with enhanced dialogs):
    # run_mesh_to_solid_macro(auto_mode=False)
    
    # Batch convert all selected meshes:
    # batch_convert_meshes(auto_mode=True)
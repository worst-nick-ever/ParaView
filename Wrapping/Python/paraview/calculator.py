r"""This module is used by vtkPythonCalculator. It encapsulates the logic
implemented by the vtkPythonCalculator to operate on datasets to compute
derived quantities.
"""

from numpy import *

from paraview import vtk
from paraview.vtk import dataset_adapter
from paraview.vtk.algorithms import *

def compute(inputs, association, expression):
    import paraview

    fd0 = inputs[0].GetAttributes(association)

    # Fill up arrays and locals variable list with
    arrays = {}
    for key in fd0.keys():
        name = paraview.make_name_valid(key)
        arrays[name] = fd0[key]

    #  build the locals environment used to eval the expression.
    mylocals = dict(arrays.items())
    mylocals["arrays"] = arrays
    mylocals["inputs"] = inputs
    try:
        mylocals["points"] = inputs[0].Points
    except: pass
    retVal = eval(expression, globals(), mylocals)

    return retVal

def execute(self, expression):
    """
    **Internal Method**
    Called by vtkPythonCalculator in its RequestData(...) method. This is not
    intended for use externally except from within
    vtkPythonCalculator::RequestData(...).
    """

    # Add inputs.
    inputs = []

    for index in range(self.GetNumberOfInputConnections(0)):
        inputs.append(dataset_adapter.WrapDataObject(
                self.GetInputDataObject(0, index)))

    # Setup output.
    output = dataset_adapter.WrapDataObject(self.GetOutputDataObject(0))

    if self.GetCopyArrays():
        output.GetPointData().PassData(inputs[0].GetPointData())
        output.GetCellData().PassData(inputs[0].GetCellData())

    retVal = compute(inputs, self.GetArrayAssociation(), expression)
    if retVal is not None:
        output.GetAttributes(self.GetArrayAssociation()).append(retVal,
            self.GetArrayName())

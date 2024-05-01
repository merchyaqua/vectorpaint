import tkinter as tk
from VectorPaintView import VectorPaintView
from VectorPaintController import VectorPaintController
from VectorPaintModel import VectorPaintModel

root = tk.Tk()

model = VectorPaintModel()
controller = VectorPaintController(model)
view = VectorPaintView(root, controller, model)

root.mainloop()
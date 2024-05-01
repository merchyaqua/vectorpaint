# ============================================================
#
#   VectorPaintController does the application logic
#
# ============================================================
class VectorPaintController:
    def __init__(self, model):
        self.model = model
        self.visiblecount = 0

    def item_added(self):
        self.visiblecount += 1 # count incremented only when item is finally in the canvas, called by the view
    # Called by any view to create a new item in the model

    def create_item(self, item_info):
        # for demonstration, set an arbitrary limit on the number of items
        if self.model.get_num_items() < 48:
            self.model.create_item(item_info)
            

        else:
            return False
        
    def delete_item(self, item_info):
        self.model.item_invisible(item_info)
    
    def undo(self):
        if self.visiblecount == 0:
            return("No items to undo")
        print("controller's got it let's undo")
        self.model.undo_action()
        self.visiblecount -= 1

    def redo(self):
        print("controller's got it let's redo")
        result = self.model.redo_action()
        if result:
            return result

        self.visiblecount += 1

    def clear(self):
        self.model.clear()

    def export(self):
        self.model.export()
    def loadfile(self):
        self.visiblecount = 0
        self.model.loadfile()
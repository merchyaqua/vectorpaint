import tkinter as tk


class VectorPaintView:
    def __init__(self, root_frame, controller, model):
        self.controller = controller
        self.root_frame = root_frame
        model.subscribe(self)
        self.alert = tk.Label(root_frame, text='Reached limit')

        # setup button bar
        self.colorBar = tk.Frame(root_frame, width=50, height=300, bg="Gray")
        self.colorBar.pack(side=tk.LEFT, fill=tk.Y)
        self.colors = ['Black', "Red", "Green"]
        for color in self.colors:
            x = tk.Button(self.colorBar, text=color, command=lambda colour = color: self.set_colour(colour))
            x.pack(side=tk.TOP, fill=tk.X)         
        # setup new button bar
        self.shapesBar = tk.Frame(root_frame, width=50, bg="Black")
        self.shapesBar.pack(side=tk.LEFT, fill=tk.Y)
        # add a shape button
        self.shapes = ["line", "rectangle", "oval"]
        for s in self.shapes:
            b = tk.Button(self.shapesBar, text=s, command=lambda shape = s: self.set_shape(shape))
            b.pack(side=tk.TOP, fill=tk.X)

        # setup main canvas
        self.canvas = tk.Canvas(root_frame, width=400, height=300, bg="White")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        
        self.toolBar = tk.Frame(root_frame, width=100, height=80)

        self.error = tk.Label(self.toolBar, bitmap='error')
        self.clearButton = tk.Button(self.toolBar, command=self.clear, text="clear")
        self.clearButton.pack()
        self.undoButton = tk.Button(self.toolBar, command=self.undo, text="undo")
        self.undoButton.pack()
        self.redoButton = tk.Button(self.toolBar, command=self.redo, text="Redo")
        self.redoButton.pack()
        self.export = tk.Button(self.toolBar, command=self.export, text="save")
        self.export.pack()
        self.loadfileButton = tk.Button(self.toolBar, command=self.loadfile, text="loadfile")
        self.loadfileButton.pack()

        self.toolBar.pack(side=tk.BOTTOM, fill=tk.Y)

        # hook in button events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<B1-Motion>", self.continue_draw)
        self.canvas.bind("<ButtonRelease-3>", self.undo)

        # set up view state variables
        self.currObject = None
        self.currColour = "Red"
        self.currShape = 'line'
        self.rectFixedCorner = [0,0]

    def set_colour(self, colour):
        self.currColour = colour
    def set_shape (self, shape):
        self.currShape = shape
        

    # drawing operations
    def start_draw(self, event):
        shape = self.currShape
        match shape:
            case "line":
                self.currObject = self.canvas.create_line(event.x, event.y, event.x, event.y, fill=self.currColour)
            case 'rectangle':
                self.rectFixedCorner = (event.x, event.y)
                self.currObject = self.canvas.create_rectangle(event.x, event.y, event.x, event.y,  fill=self.currColour)
            case "oval":
                self.rectFixedCorner = event.x, event.y
                self.currObject = self.canvas.create_oval(event.x, event.y, event.x, event.y,  fill=self.currColour)
    def continue_draw(self, event):
        coords_list = self.canvas.coords(self.currObject)
        new_coords_list = coords_list[:]
        
        
        if self.rectFixedCorner and self.rectFixedCorner[0] > event.x:
            new_coords_list[2] = self.rectFixedCorner[0] # new ending
            new_coords_list[0] = event.x # new starting
        else:
            if event.x >0:
                new_coords_list[2] = event.x
            else:
                new_coords_list[2] = 1
                print(new_coords_list)



        if self.rectFixedCorner and self.rectFixedCorner[1] > event.y:
            new_coords_list[3] = self.rectFixedCorner[1] # new ending
            new_coords_list[1] = event.y # new starting
        else:
            if event.y >0:
                new_coords_list[3] = event.y
            else:
                new_coords_list[3] = 1
                print(new_coords_list)

        self.canvas.coords(self.currObject, new_coords_list)
    def stop_draw(self, event):
        coords_list = self.canvas.coords(self.currObject)
        result = self.controller.create_item(
            {
                "type": self.currShape,
                "start": coords_list[:2],
                "end": coords_list[2:],
                "colour": self.currColour                
            }
        )
        if not result:
             # too bad exceeded
            self.alert.pack()

        self.canvas.delete(self.currObject)
        self.rectFixedCorner = 0, 0
        self.currObject = None
    def undo(self):
        print("we're gonna undo")
        result = self.controller.undo()
        if result:
            self.alert.pack_forget()
            self.alert = tk.Label(self.root_frame, text=result)
            self.alert.pack()
    def redo(self):
        print("we're gonna redo")
        result = self.controller.redo()
        if result:
            print(result)
            self.alert.pack_forget()
            self.alert = tk.Label(self.root_frame, text=result)
            self.alert.pack()
    def destroy(self):
        self.canvas.delete("all")
    def clear(self):
        self.controller.clear()


    # model-called functions - model always passes its own object ids and you can retrieve using find with tag. this works because i never delete objects so IDs remain constant, deleted or not
    def item_added(self, item_info):
        args = {
            'x0': item_info["start"][0],
            'y0': item_info["start"][1],
            'x1': item_info["end"][0], 
            'y1': item_info["end"][1],
            'fill': item_info["colour"],
            'tags': [str(item_info["objectID"])]
        }
        match item_info["type"]:
            case "line":
                self.canvas.create_line(item_info["start"][0],item_info["start"][1],
            item_info["end"][0], 
            item_info["end"][1],
            fill=item_info["colour"],
            tags=[item_info["objectID"]])
            case "rectangle":
                self.canvas.create_rectangle(item_info["start"][0],item_info["start"][1],
            item_info["end"][0], 
            item_info["end"][1],
            fill=item_info["colour"],
            tags=[item_info["objectID"]])
            case "oval":
                self.canvas.create_oval(item_info["start"][0],item_info["start"][1],
            item_info["end"][0], 
            item_info["end"][1],
            fill=item_info["colour"],
            tags=[item_info["objectID"]])
                
        print("object of tag " + str(item_info["objectID"]) +" is created")
        self.controller.item_added()     
        
    def item_removed(self, item_id):
        self.canvas.delete(item_id)

    def item_visible(self, item_id):
        item = self.canvas.find_withtag(item_id)
        self.canvas.itemconfigure(item, state ="normal")

    def item_invisible(self, item_id):
        print(item_id)
        item = self.canvas.find_withtag(str(item_id))
        print(item)
        print(self.canvas.find_all())
        self.canvas.itemconfigure(item, state="hidden")

    def disable_buttons(self):
        self.buttonBar.pack_forget()
        self.alert.pack()

    # file operations.
        
    def export(self):
        self.controller.export()
    def loadfile(self):
        self.controller.loadfile()
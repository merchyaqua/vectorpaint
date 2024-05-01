# ============================================================
#
#   VectorPaintModel holds the data for the vector image
#
# ============================================================
class VectorPaintModel:
    class OperationStack:
        ''' each item is stored with its id and its operation - create or delete '''
        def __init__(self, model) -> None:

            self.model = model
            self.stack = []
            self.undone_stack = []
        
        def addOperation(self, op):
            self.stack.append(op)
        def undo(self):
            print("opstack: oh i've been asked to undo")
            try:
                bye = self.stack.pop()
            except IndexError:
                return "what the hell"
            # ignore the delete bit. not implemented
            if bye["operation"] == "create" or bye['operation'] == "visible":
                self.model.item_invisible(bye)
            elif bye["operation"] == 'delete':
                self.model.item_visible(bye)
            self.undone_stack.append(bye)


        def redo(self):
            print("opstack: oh i've been asked to redo")

            try:
                
                hi = self.undone_stack.pop()
                self.addOperation(hi)
            except IndexError:
                print("um no")
                return ("Nothing to redo")
            if hi["operation"] == "create" or hi['operation'] == "visible":
                self.model.item_visible(hi)
            elif hi["operation"] == 'delete':
                self.model.item_invisible(hi)

    class ProjectFileRW:
        # handles direct file io. 
        def __init__(self, model):
            self.filename = "project.vp"
            self.opfilename = "opstack.vp"

            self.file = None
            self.model = model
        def read(self):
            # reads each line and return it as a model-compatible format, with each id mapped to item info.
            items = []
            with open(self.filename, "r") as f:
                while line := f.readline():
                    objectID, typ, start, end, colour, visible = line.split('|')
                    start = list(map(float, start.split(',')))
                    end = list(map(float, end.split(',')))

                    item = {objectID: {'type': typ, 'start': start, 'end': end, 'colour': colour, 'objectID': objectID, 'Visible': bool(int(visible))}}
                    items.append(item) # the existence of this class is slightly redundant in fact
            opstack = []
            undonestack = []
            undone = False
            with open(self.opfilename, "r") as f:
                while line := f.readline().strip():
                    if line == "UNDONE" :
                        undone = True
                        continue
                    objectID, operation = line.split('|')
                    if not undone:
                        opstack.append({"objectID": objectID, "operation": operation})
                    else:
                        undonestack.append({"objectID": objectID, "operation": operation})


                    

            return items, opstack, undonestack

        def write(self):
            # turn the model's items and opstack into file content, 
            def stringifyCoords(c):
                return ','.join(map(str, c))
            
            items = self.model.items
            opstack = self.model.opstack
            with open(self.filename, "w") as f:
                for ID in items:
                    i = items[ID]
                    # id, type, start, end, colour, visible 
                    l = [str(ID), 
                         i["type"], 
                         stringifyCoords(i["start"]), 
                         stringifyCoords(i["end"]), 
                         i["colour"],
                         str(int(i["Visible"]))
                         ]
                    f.write("|".join(l))
                    f.write('\n')
                    
            with open(self.opfilename, 'w') as f:
                f.writelines(str(item["objectID"]) + '|' + item['operation']+"\n" for item in opstack.stack)
                f.write("UNDONE\n")
                f.writelines(str(item["objectID"]) + '|' + item['operation']+"\n" for item in opstack.undone_stack)


    def __init__(self):
        # list of objects to tell about any changes
        self.observers = []

        # counter for unique id for any new items
        self.next_item_id = 50

        # the list of items in the picture = id tied to a dict:item_info.
        self.items = {}

        self.opstack = self.OperationStack(self)

        self.projectfilewriter = self.ProjectFileRW(self)
    
    def undo_action(self):
        print("aight let's let the opstack know")
        self.opstack.undo()
    def redo_action(self):
        print("aight let's let the opstack know")
        return self.opstack.redo()
        
    # called by an instance that wants to know about any changes
    def subscribe(self, observer):
        self.observers.append(observer)

    # returns the number of items in the picture
    def get_num_items(self):
        return len(self.items)

    # creates an item within the model
    def create_item(self, item_info):
        item_info["objectID"] = "#" + str(self.next_item_id)
        self.next_item_id += 2
        self.opstack.addOperation({
            "objectID": item_info["objectID"],
            "operation": "create"
        })
        item_info["Visible"] = True

        self.items[item_info["objectID"]] = item_info
        # self.opstack.undone_stack = [] # clear this branch
        for observer in self.observers:
            observer.item_added(item_info) # the callback

    # not sure if this is actually called by anything
        
    def delete_item(self, item_id):
        self.items[item_id]["Visible"]= False
        
        for observer in self.observers:
            observer.item_deleted(item_id)

    def item_invisible(self, op_info):
        # self.opstack.addOperation({
        #     "id": op_info["id"],
        #     "operation": "delete"
        # })
        print(op_info, " is invisible in model")
        self.items[op_info["objectID"]]["Visible"]= False

        for observer in self.observers:
            observer.item_invisible(op_info["objectID"])

    def item_visible(self, op_info):
        # self.opstack.addOperation({
        #     "id": op_info["id"],
        #     "operation": "create"
        # })
        print(op_info, " is now visible in model")
        self.items[op_info["objectID"]]["Visible"]= True 


        for observer in self.observers:
            observer.item_visible(op_info["objectID"])
    def clear(self):
        while len(self.opstack.stack) >0:
            self.undo_action()

    def export(self):
        # we need classes! 
        print(self.items)
        self.projectfilewriter.write()

    def loadfile(self):
        # get the stuff and set to self then for each thing, recreate the process.
        # go through each item and create it. then restore the opstack.
        # items e.g. {2: {'type': 'line', 'start': [129.0, 57.0], 'end': [208.0, 192.0], 'colour': 'Red', 'objectID': 2, 'Visible': False}, 4:{...}}
        items, opstack, undonestack = self.projectfilewriter.read()
        # undonestack.reverse()
        undone_elements = list(map(lambda x: x["objectID"], undonestack)) 
        for thing in items: # well do i really need the opstack stored if i can just recreate all?
            item_info = list(thing.values())[0] # just that one value (a dict)
            self.create_item(item_info)
            if item_info["objectID"] in undone_elements: # I really overcomplicated this
                self.undo_action()
        self.opstack.undone_stack.reverse()# it had the redo order upside down due to the way i re-enacted undos

        


    '''
    What we will need:
    - a file reader/writer
    - a way to represent opstack info
    - a way to represent which items exist, with their visible/invisible states
    self.items will contain dictionaries of item_info AND their states. When an item is made invisible,
    we index into the item list and change its state.
    All of this is saved as-is - down the list of items.
    This is to preserve all the order, and would be much less hassle if I went and changed my model ID tags to the #01 format,
    but this invisible/visible thing is built all to bypass this. So we'll roll with it. ugh


    When the file is loaded, 
    the model gets a file reader and reads the file.
    for each item dict that is retrieved, in order,
    each item is recreated using the item_added function in the view. the ids should line up.
    Sample file that contains a blue rectangle visible and a red oval that has been undone:

    
    *
    '''

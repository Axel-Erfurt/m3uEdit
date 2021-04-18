#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib

CSS = """
#mywindow {
 background: #eee;
}

#csv-view {
  color: #222;
  font-family: "Noto Sans";
  font-size: 9pt;
}
#csv-view :selected {
  background: #bdf;
  color: #222;
}
#csv-view header button { 
 color: #222;
 background: #ddd;
 font-weight: bold; 
 border: 0.1pt solid #111;
 }
#csv-view :hover {
 background: #444;
 color: #ace;
}
#btn_open:hover ,#btn_save:hover, 
#btn_addrow:hover, #btn_copy_row:hover 
#btn_paste_row:hover {
 background: #abc;
}
#csv-view row:nth-child(odd) {
    background-color: shade(@base_normal, 0.93);
}
#sublabel {
 font-size: 8pt;
 color: #444;
}
tooltip {
 font-size: 9pt;
 background: #a5dcff;
 color: #444444;
}
#searchfield {
 font-size: 9pt;
 background: #eeeeec;
 color: #444444;
}
#selcombo {
 font-size: 9pt;
}
"""    

class TreeViewFilterWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="m3uEditor")
        self.set_name("mywindow")
        self.set_border_width(4)
        self.current_file = ""
        self.column_count = 0
        self.is_changed = False
        self.connect("delete-event", self.on_close)
        self.cb = ""
        self.m3u_file = ""
        self.csv_file = ""
        self.fname = ""
        self.my_liststore = None
        
        # box
        self.vbox = Gtk.Box(orientation=1, vexpand=True)
        self.add(self.vbox)
        
        self.hbox = Gtk.Box(orientation=0)
        
        # open button
        self.btn_open = Gtk.Button.new_from_icon_name("document-open", 2)
        self.btn_open.set_name("btn_open")
        self.btn_open.set_tooltip_text("Open File")
        self.btn_open.set_hexpand(False)
        self.btn_open.set_relief(2)
        self.btn_open.connect("clicked", self.on_open_file)
        
        self.hbox.pack_start(self.btn_open, False, False, 1)
        
        # save button
        self.btn_save = Gtk.Button.new_from_icon_name("document-save", 2)
        self.btn_save.set_name("btn_save")
        self.btn_save.set_tooltip_text("Save current File")
        self.btn_save.set_hexpand(False)
        self.btn_save.set_relief(2)
        self.btn_save.connect("clicked", self.on_save_file)
        
        self.hbox.pack_start(self.btn_save, False, False, 1)

        # save as button
        self.btn_save_as = Gtk.Button.new_from_icon_name("document-save-as", 2)
        self.btn_save_as.set_name("btn_save")
        self.btn_save_as.set_tooltip_text("Save As ...")
        self.btn_save_as.set_hexpand(False)
        self.btn_save_as.set_relief(2)
        self.btn_save_as.connect("clicked", self.on_save_file_as)
        
        self.hbox.pack_start(self.btn_save_as, False, False, 1)
        
        # separator
        sep = Gtk.Separator()
        self.hbox.pack_start(sep, False, False, 1)
        
        # add row button
        self.btn_addrow = Gtk.Button.new_from_icon_name("add", 2)
        self.btn_addrow.set_name("btn_addrow")
        self.btn_addrow.set_tooltip_text("insert row below selelected row")
        self.btn_addrow.set_hexpand(False)
        self.btn_addrow.set_relief(2)
        self.btn_addrow.connect("clicked", self.on_add_row)
        
        self.hbox.pack_start(self.btn_addrow, False, False, 1)
        
        # remove row button
        self.btn_remove_row = Gtk.Button.new_from_icon_name("remove", 2)
        self.btn_remove_row.set_name("btn_remove_row")
        self.btn_remove_row.set_tooltip_text("remove selelected row")
        self.btn_remove_row.set_hexpand(False)
        self.btn_remove_row.set_relief(2)
        self.btn_remove_row.connect("clicked", self.on_remove_row)
        
        self.hbox.pack_start(self.btn_remove_row, False, False, 1)
        
        sep = Gtk.Separator()
        self.hbox.pack_start(sep, False, False, 1)

        # row up button
        self.btn_row_up = Gtk.Button.new_from_icon_name("up", 2)
        self.btn_row_up.set_name("btn_row_up")
        self.btn_row_up.set_tooltip_text("move selelected row up")
        self.btn_row_up.set_hexpand(False)
        self.btn_row_up.set_relief(2)
        self.btn_row_up.connect("clicked", self.on_row_up)
        
        self.hbox.pack_start(self.btn_row_up, False, False, 1)
        
        # row down button
        self.btn_row_down = Gtk.Button.new_from_icon_name("down", 2)
        self.btn_row_down.set_name("btn_row_down")
        self.btn_row_down.set_tooltip_text("move selelected row down")
        self.btn_row_down.set_hexpand(False)
        self.btn_row_down.set_relief(2)
        self.btn_row_down.connect("clicked", self.on_row_down)
        
        self.hbox.pack_start(self.btn_row_down, False, False, 1)
        
        sep = Gtk.Separator()
        self.hbox.pack_start(sep, False, False, 1)
        
        # table search column selector
        items = ['tvg-name', 'group-title', 'tvg-logo', 'tvg-id', 'url']
        self.column_selector = Gtk.ComboBoxText()
        self.column_selector.set_name("selcombo")
        for item in items:
            self.column_selector.append_text(item)
        self.column_selector.set_active(0)
        self.column_selector.connect('changed', self.set_search_column)
        self.column_selector.set_tooltip_text("select column for internal search\nsearch by typing if table has focus")
        self.hbox.pack_start(self.column_selector, False, False, 1)

        # find field
        self.find_field = Gtk.SearchEntry()
        self.find_field.set_placeholder_text("find ...")
        self.find_field.connect("activate", self.replace_in_table)
        self.find_field.set_vexpand(False)
        self.hbox.pack_start(self.find_field, False, False, 1)

        # replace field
        self.replace_field = Gtk.SearchEntry()
        self.replace_field.set_placeholder_text("replace with ...")
        self.replace_field.set_vexpand(False)
        self.hbox.pack_start(self.replace_field, False, False, 1)
        
        self.vbox.pack_start(self.hbox, False, False, 1)  
  
        # replace button
        self.btn_replace_all = Gtk.Button.new_from_icon_name("edit-find-replace", 2)
        self.btn_replace_all.set_name("btn_replace_all")
        self.btn_replace_all.set_tooltip_text("replace all in selected column")
        self.btn_replace_all.set_hexpand(False)
        self.btn_replace_all.set_relief(2)
        self.btn_replace_all.connect("clicked", self.replace_in_table)  
        
        self.hbox.pack_start(self.btn_replace_all, False, False, 1)
        
        # replace all column selector
        items = ['tvg-name', 'group-title']
        self.replace_selector = Gtk.ComboBoxText()
        self.replace_selector.set_name("replace_selector")
        for item in items:
            self.replace_selector.append_text(item)
        self.replace_selector.set_active(0)
        self.replace_selector.connect('changed', self.set_search_column)
        self.replace_selector.set_tooltip_text("select column for replace all")
        self.hbox.pack_start(self.replace_selector, False, False, 1)
        
        # search field
        self.search_field = Gtk.SearchEntry()
        self.search_field.set_name("searchfield")
        self.search_field.set_placeholder_text("filter")
        self.search_field.connect("activate", self.on_filter_clicked)
        self.search_field.connect("search-changed", self.on_filter_changed)
        self.search_field.set_tooltip_text("filter table by search term")
        self.search_field.set_vexpand(False)
        self.hbox.pack_end(self.search_field, False, False, 1)
        
        self.vbox.pack_start(self.hbox, False, False, 1)

        # treeview
        self.treeview = Gtk.TreeView()
        self.treeview.set_name("csv-view")
        self.treeview.set_grid_lines(3)
        self.treeview.set_reorderable(True)
        self.treeview.connect("drag-data-received", self.drag_data_received)
        self.treeview.connect("cursor-changed", self.onSelectionChanged)
        self.treeview.connect("button-press-event", self.on_pressed)

        self.my_treelist = Gtk.ScrolledWindow()
        self.my_treelist.add(self.treeview)
        self.vbox.pack_start(self.my_treelist, True, True, 5)
        
        # status label
        self.status_label = Gtk.Label(label="Info")
        self.status_label.set_name("sublabel")
        self.vbox.pack_end(self.status_label, False, False, 1)

        # style
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(CSS.encode()))
        style = self.treeview.get_style_context()
        screen = Gdk.Screen.get_default()
        priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        style.add_provider_for_screen(screen, provider, priority)
        
    def set_search_column(self, *args):
        index = self.column_selector.get_active()
        self.treeview.set_search_column(index)
        
    def replace_in_table(self, *args):
        index = int(self.replace_selector.get_active())
        search_term = self.find_field.get_text()
        replace_term = self.replace_field.get_text()
        #for row in self.my_liststore:
        #    #print(row[:])
        if index == 0:
            column_number = 0
            iter_child = self.my_liststore.get_iter_first()
            tree_path = None
            while iter_child:
                if (search_term in self.my_liststore.get_value(iter_child, column_number)):
                    tree_path = self.my_liststore.get_path(iter_child)
                    print(tree_path, column_number)
                    value = self.my_liststore.get_value(iter_child, column_number).replace(search_term, replace_term)
                    print(value)
                    self.my_liststore.set_value(iter_child, column_number, value)
                iter_child = self.my_liststore.iter_next(iter_child)
        elif index == 1:
            column_number = 1
            iter_child = self.my_liststore.get_iter_first()
            tree_path = None
            while iter_child:
                if (search_term in self.my_liststore.get_value(iter_child, column_number)):
                    tree_path = self.my_liststore.get_path(iter_child)
                    print(tree_path, column_number)
                    value = self.my_liststore.get_value(iter_child, column_number).replace(search_term, replace_term)
                    print(value)
                    self.my_liststore.set_value(iter_child, column_number, value)
                iter_child = self.my_liststore.iter_next(iter_child)
        self.is_changed = True

            
        
    def maybe_saved(self, *args):
        print("is modified", self.is_changed)
        md = Gtk.MessageDialog(title="m3uEditor", message_type=Gtk.MessageType.QUESTION, 
                                text="The document was changed.\n\nSave changes?", 
                                parent=None)
        md.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
             "Yes", Gtk.ResponseType.YES, "No", Gtk.ResponseType.NO)
             
        response = md.run()
        if response == Gtk.ResponseType.YES:
            ### save
            self.on_save_file()
            md.destroy()
            return False
        elif response == Gtk.ResponseType.NO:
            md.destroy()
            return False
        elif response == Gtk.ResponseType.CANCEL:
            md.destroy()
            return True
        md.destroy()
        
    def maybe_saved_on_open(self, *args):
        print("is modified", self.is_changed)
        md = Gtk.MessageDialog(title="m3uEditor", message_type=Gtk.MessageType.QUESTION, 
                                text="The document was changed.\n\nSave changes?", 
                                parent=None)
        md.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
             "Yes", Gtk.ResponseType.YES, "No", Gtk.ResponseType.NO)
             
        response = md.run()
        if response == Gtk.ResponseType.YES:
            md.destroy()
            return 1
        elif response == Gtk.ResponseType.NO:
            md.destroy()
            return 2
        elif response == Gtk.ResponseType.CANCEL:
            md.destroy()
            return 3
        md.destroy()
        
    def on_close(self, *args):
        print("goodbye ...")
        print(f"{self.current_file} changed: {self.is_changed}")
        if self.is_changed:
            b = self.maybe_saved()
            print (f"close: {b}")
            if b: 
                return True
            else:
                Gtk.main_quit()
        else:
            Gtk.main_quit()
        
    def on_add_row(self, *args):
        model, paths = self.treeview.get_selection().get_selected_rows()
        if paths:
            index = self.treeview.get_selection().get_selected_rows()[1][0][0]
            self.my_liststore.insert(index + 1)
            self.is_changed = True
        
    def on_remove_row(self, *args):
        model, paths = self.treeview.get_selection().get_selected_rows()
        if paths:
            for path in paths:
                iter = self.my_liststore.get_iter(path)
                self.my_liststore.remove(iter)
            self.is_changed = True
                   
    def on_pressed(self, trview, event):
        if not self.my_liststore == None and len(self.my_liststore) > 0:
            path, col, x, y = trview.get_path_at_pos(event.x, event.y)
            if path and col and x and y:
                self.column_index = col.colnr
                self.path = path
        
    def onSelectionChanged(self, *args):
        model, pathlist = self.treeview.get_selection().get_selected()
        if pathlist:
            self.value_list = []
            for x in range(self.column_count):
                self.value_list.append(model[pathlist][x])
                
    def on_row_up(self, *args):
        self.move_selected_items_up(self.treeview)
        self.is_changed = True

    def move_selected_items_up(self, treeView):
        selection = treeView.get_selection()
        model, selected_paths = selection.get_selected_rows()
        for path in selected_paths:
            index_above = path[0]-1
            if index_above < 0:
                return
            self.my_liststore.move_before(self.my_liststore.get_iter(path), self.my_liststore.get_iter((index_above,)))
            
    def on_row_down(self, *args):
        self.move_selected_items_down(self.treeview)
        self.is_changed = True

    def move_selected_items_down(self, treeView):
        selection = treeView.get_selection()
        model, selected_paths = selection.get_selected_rows()
        for path in selected_paths:
            index_above = path[0]+1
            if index_above < 0:
                return
            self.my_liststore.move_after(self.my_liststore.get_iter(path), self.my_liststore.get_iter((index_above,)))
        
    def on_open_file(self, *args):
       # save question
       if self.is_changed:
           b = self.maybe_saved_on_open()
           if b == 1:
               self.on_save_file()
               self.open_file()
           elif b == 2:
               self.is_changed = False
               self.open_file()
           else:
               return
       else:
           self.open_file()

    def open_file(self, *args):
           dlg = Gtk.FileChooserDialog(title="Please choose a file", parent=None, action = 0)
           dlg.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                     "Open", Gtk.ResponseType.OK)
           docs = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
           dlg.set_current_folder(docs)     
           filter = Gtk.FileFilter()
           filter.set_name("M3U Files")
           filter.add_pattern("*.m3u")
           dlg.add_filter(filter)
           response = dlg.run()

           if response == Gtk.ResponseType.OK:
               self.current_file = (dlg.get_filename())
               self.m3u_file = self.current_file
               self.convert_to_csv()
               self.load_into_table(self.csv_file)
               self.current_file = self.csv_file

           dlg.destroy()               
       
    def load_into_table(self, csv_file, *args):
        self.search_field.set_text("")
        self.current_filter_text = ""
        for column in self.treeview.get_columns():
            self.treeview.remove_column(column)
        my_list = []
        my_csv = open(csv_file, 'r').read().splitlines()
        self.column_count = len(my_csv[0].split('\t'))
        self.my_liststore = Gtk.ListStore(*[str]* self.column_count)
            
        for i, column_title in enumerate(my_csv[0].split('\t')):
            renderer = Gtk.CellRendererText()
            renderer.set_property('editable', True)
            renderer.connect("edited", self.text_edited)
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.colnr = i
            self.treeview.append_column(column)

        for line in my_csv[1:]:
            row = line.split('\t')
            my_list.append(tuple(row))
            
        for line_value in my_list:
            self.my_liststore.append(list(line_value))
                 
        self.my_filter = self.my_liststore.filter_new()
        self.my_filter.set_visible_func(self.visible_cb)
        self.treeview.set_model(self.my_filter)
        self.treeview.set_enable_search(True)
        #self.treeview.set_search_equal_func()
        self.set_title(csv_file.rpartition("/")[2].rpartition(".")[0])
        self.status_label.set_text(f'{csv_file} loaded')
        self.is_changed = False

    def on_save_file_as(self, *args):
       dlg = Gtk.FileChooserDialog(title="Please choose a file", parent=None, action = 1)
       dlg.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                 "Save", Gtk.ResponseType.OK)
       dlg.set_do_overwrite_confirmation(True)          
       filter = Gtk.FileFilter()
       filter.set_name("M3U Files")
       filter.add_pattern("*.m3u")
       dlg.add_filter(filter)
       
       dlg.set_current_name(self.fname.replace(".csv", ".m3u"))
       response = dlg.run()

       if response == Gtk.ResponseType.OK:
            infile = (dlg.get_filename())
            print(infile)
            # model to csv_file
            list_string = []        
            for node in self.my_liststore:
                d = []
                for column in range(self.column_count):
                    the_node = node[column]
                    if the_node == None:
                        the_node = ""
                    d.append(the_node)
                list_string.append(d)
            with open("/tmp/tmp.csv", 'w') as f:
                for line in list_string:
                    value = "\t".join(line)
                    f.write(f'{value}\n')
            m3u_content = self.convert_to_m3u_2()
            with open(infile, 'w') as f:        
                f.write(m3u_content)
                self.is_changed = False 
                self.status_label.set_text(f'{infile} saved')
                print(f'{infile} saved')
       else:
           print("None")
       dlg.destroy()   

    def on_save_file(self, *args):
        if self.m3u_file == "":
            self.on_save_file_as()
        else:
            # model to csv_file
            list_string = []        
            for node in self.my_liststore:
                d = []
                for column in range(self.column_count):
                    the_node = node[column]
                    if the_node == None:
                        the_node = ""
                    d.append(the_node)
                list_string.append(d)

            with open(self.csv_file, 'w') as f:
                for line in list_string:
                    value = "\t".join(line)
                    f.write(f'{value}\n')
            m3u_content = self.convert_to_m3u()
            with open(self.m3u_file, 'w') as f:        
                f.write(m3u_content)
                self.is_changed = False 
                self.status_label.set_text(f'{self.m3u_file} saved')
                print(f'{self.m3u_file} saved')
              
    def convert_to_m3u(self):
        mylist = open(self.csv_file, 'r').read().splitlines()
        group = ""
        ch = ""
        url = ""
        id = ""
        logo = ""
        m3u_content = ""

        headers = ['tvg-name', 'group-title', 'tvg-logo', 'tvg-id', 'url']
        m3u_content += "#EXTM3U\n"

        for x in range(len(mylist)):
            line = mylist[x].split('\t')
            ch = line[0]
            group = line[1]
            logo = line[2]
            id = line[3]
            url = line[4]
            
            m3u_content += f'#EXTINF:-1 tvg-name="{ch}" group-title="{group}" tvg-logo="{logo}" tvg-id="{id}",{ch}\n{url}\n'
        
        return m3u_content
        
    def convert_to_m3u_2(self):
        mylist = open(self.csv_file, 'r').read().splitlines()
        group = ""
        ch = ""
        url = ""
        id = ""
        logo = ""
        m3u_content = ""

        headers = ['tvg-name', 'group-title', 'tvg-logo', 'tvg-id', 'url']
        m3u_content += "#EXTM3U\n"

        for x in range(1, len(mylist)):
            line = mylist[x].split('\t')
            ch = line[0]
            group = line[1]
            logo = line[2]
            id = line[3]
            url = line[4]
            
            m3u_content += f'#EXTINF:-1 tvg-name="{ch}" group-title="{group}" tvg-logo="{logo}" tvg-id="{id}",{ch}\n{url}\n'
        
        return m3u_content
            
    def text_edited(self, cellrenderertext, treepath, text):
        column = self.column_index
        self.my_liststore[treepath][column] = text
        self.is_changed = True
        
    def drag_data_received(self, dest, selection_data, *args):
        print(dest.get_drag_dest_row())

    def my_filter_func(self, model, iter, data):
        if (
            self.current_filter_text is None
            or self.current_filter_text == "None"
        ):
            return True
        else:
            return model[iter][0] == self.current_filter_text

    def on_filter_clicked(self, widget):
        self.current_filter_text = widget.get_text()
        self.my_filter.refilter()

    def visible_cb(self, model, iter, data=None):
        search_query = self.search_field.get_text().lower()
        active_category = 0
        search_in_all_columns = True

        if search_query == "":
            return True

        if search_in_all_columns:
            for col in range(0,self.treeview.get_n_columns()):
                value = model.get_value(iter, col)
                if (search_query.lower() in  value
                    or search_query.upper() in  value
                    or search_query.title() in  value):
                    return True

            return False

        value = model.get_value(iter, active_category).lower()
        #return True if value.startswith(search_query) else False
        return True if search_query in value else False
        
    def on_filter_changed(self, *args):
        if self.search_field.get_text() == "":
            self.on_filter_clicked(self.search_field)
    
    def convert_to_csv(self):
        mylist = open(self.m3u_file, 'r').read().splitlines()

        headers = ['tvg-name', 'group-title', 'tvg-logo', 'tvg-id', 'url']
        group = ""
        ch = ""
        url = ""
        id = ""
        logo = ""
        csv_content = ""
        csv_content += '\t'.join(headers)
        csv_content += "\n"
        for x in range(1, len(mylist)-1):
            line = mylist[x]
            nextline = mylist[x+1]
            if line.startswith("#EXTINF") and not "**********" in line:
                if 'tvg-name="' in line:
                    ch = line.partition('tvg-name="')[2].partition('"')[0]
                elif 'tvg-name=' in line:
                    ch = line.partition('tvg-name=')[2].partition(' tvg')[0]
                else:
                    ch = line.rpartition(',')[2]        
                if ch == "":
                    ch = "No Name"
                ch = ch.replace('"', '')
                    
                if 'group-title="' in line:
                    group = line.partition('group-title="')[2].partition('"')[0]

                elif "group-title=" in line:
                    group = line.partition('group-title=')[2].partition(' tvg')[0]
                else:
                    group = "TV"
                group = group.replace('"', '')        
                
                if 'tvg-id="' in line:
                    id = line.partition('tvg-id="')[2].partition('"')[0]
                elif 'tvg-id=' in line:
                    id = line.partition('tvg-id=')[2].partition(' ')[0]
                else:
                    id = ""
                id = id.replace('"', '')
                
                url = nextline
                if 'tvg-logo="' in line:
                    logo = line.partition('tvg-logo="')[2].partition('"')[0]
                elif 'tvg-logo=' in line:
                    logo = line.partition('tvg-logo=')[2].partition(' ')[0]        
                else:
                    logo = ""            
                csv_content += (f'{ch}\t{group}\t{logo}\t{id}\t{url}\n')
        self.fname = self.m3u_file.rpartition("/")[2].replace(".m3u", ".csv")
        self.csv_file = f'/tmp/{self.fname}'
        with open(self.csv_file, 'w') as f:        
            f.write(csv_content)
            
win = TreeViewFilterWindow()
win.connect("destroy", Gtk.main_quit)
win.set_size_request(600, 300)
win.move(0, 0)
win.show_all()
win.resize(1000, 600)
Gtk.main()

class Tag:
    
    def __init__(self, tag: str, indices: list[int, int]) -> None:
        
        if tag.strip()[0] != "<" or tag.strip()[-1] != ">":
            raise Exception("Tag needs to end with '<' or '>'.")
        self.html_tag = tag
        self.tag = tag
        
        self.indices = indices
        
        self.has_end_tag = False
        
        self.data = None
        
        self.attrs = self.create_attrs(self.tag)
        
        self.parent = None
        self.children = None
    
    
    def create_attrs(self, tag: str) -> dict | None:
        
        tag = tag[1:-1]
        
        tag = tag.strip()
        
        index = tag.find(" ")
        if index == -1 or tag[0] == "/":
            tag = tag.split(" ")
            self.tag = "".join(tag)
            return None
        else:
            self.tag = tag[:index].strip()
        
        tag = tag[index+1:].strip()
        
        attrs = {}
        lindex = 0
        key = ""
        value = ""
        final_key = ""
        final_value = None
        for index, char in enumerate(tag):
            if char == "=" and final_key == "":
                final_key = key.strip()
            elif (char == "\"" or char=="\'") and final_key != "":
                if final_value is None:
                    final_value = ""
                else:
                    attrs[final_key] = value
                    key = ""
                    value = ""
                    final_key = ""
                    final_value = None
            elif key != "" and final_value is None and (char == " " or index == len(tag)-1):
                if index != len(tag)-1:
                    for c in tag[index:]:
                        if c == "=" or c == "\"" or c == "\'":
                            single_arg = False
                            break
                        elif c != " ":
                            single_arg = True
                            break
                    if single_arg:
                        attrs[key.strip()] = True
                        key = ""
                        value = ""
                        final_key = ""
                        final_value = None
                else:
                    attrs[(key+char).strip()] = True
                    key = ""
                    value = ""
                    final_key = ""
                    final_value = None
            elif final_key == "":
                key += char
            elif final_value is not None and final_key != "":
                value += char
        
        return attrs
    
    
    def __repr__(self) -> str:
        
        string = f"<{self.tag} "
        
        if self.attrs == None:
            return string[:-1] + ">"
        
        for attr in self.attrs:
            if self.attrs.get(attr) is True:
                string += f"{attr} "
            else:
                string += f"{attr}=\"{self.attrs.get(attr)}\" "
        
        return string[:-1] + ">"


class HTML:
    
    def __init__(self, html: str) -> None:
        
        self.html = html
        self.filtered_html = None
        self.doctype = None
        self.root = None
        self.tags = []
        
        self.do_stuff()
    
    
    def do_stuff(self) -> None:
        
        html = self.html
        html = html.strip()[1:].strip()
        
        if html[:9].lower().strip() == "!doctype":
            end = html[:].find(">")
            self.doctype = html[9:end].strip()
       
            html = html[end+1:].strip()
        else:
            html = self.html
        
        self.filtered_html = html
        
        tag_indices = []
        for index, char in enumerate(html):
            if index == len(html) - 1:
                if char == "<" and html[index-1] != "<":
                    tag_indices.append((index,))
                elif char == ">" and html[index-1] != ">":
                    for i in range(len(tag_indices)-1, -1, -1):
                        if len(tag_indices[i]) != 2:
                            tag_indices[i] = (tag_indices[i][0], index)
                            break
            else:
                if char == "<" and html[index-1] != "<" and html[index+1] != "<":
                    tag_indices.append((index,))
                elif char == ">" and html[index-1] != ">" and html[index+1] != ">":
                    for i in range(len(tag_indices)-1, -1, -1):
                        if len(tag_indices[i]) != 2:
                            tag_indices[i] = (tag_indices[i][0], index)
                            break
        
        for index, indices in enumerate(tag_indices):
            if index == 0:
                if not HTML.is_end_tag(html[indices[0]:indices[1]+1]):
                    self.root = Tag(html[indices[0]:indices[1]+1], indices)
                    self.tags.append(self.root)
                else:
                    raise Exception("Root tag is an end tag?")
            else:
                self.tags.append(Tag(html[indices[0]:indices[1]+1], indices))
        
        for tag in self.tags:
            if f"/{tag.tag}" in [t.tag for t in self.tags]:
                tag.has_end_tag = True
            else:
                tag.has_end_tag = False
        
        delete = []
        for index, tag in enumerate(self.tags):
            if HTML.is_end_tag(tag):
                delete.append(index)
            else:
                tag.children = HTML.find_children(tag, self.tags[index+1:])
        
        for index, tag in enumerate(self.tags):
            if tag.children is None and tag.has_end_tag and not HTML.is_end_tag(tag):
                if html[tag_indices[index][1]+1 : tag_indices[index+1][0]].strip() != "":
                    tag.data = html[tag_indices[index][1]+1 : tag_indices[index+1][0]].strip()
        
        self.tags = [self.tags[i] for i in range(len(self.tags)) if not i in delete]
    
    
    def is_end_tag(tag: str | Tag) -> bool:
        
        if isinstance(tag, Tag):
            tag = tag.__repr__()
        
        tag = tag[1:-1]
        
        tag = tag.strip()
        
        if tag[0] == "/":
            return True
        
        return False
    
    
    def find_children(tag: Tag, tags: list[Tag]) -> list[Tag] | None:
        
        if not tag.has_end_tag:
            return None
        
        children = []
        offset = 0
        same_offset = 0
        for t in tags:
            if tag.tag == t.tag:
                same_offset += 1
            if t.tag == f"/{tag.tag}":
                same_offset -= 1
            if same_offset == -1:
                break
            
            if offset == 0:
                children.append(t)
                t.parent = tag
                if t.has_end_tag:
                    offset = 1
            elif offset == 1 and HTML.is_end_tag(t):
                offset = 0
            elif not HTML.is_end_tag(t):
                if t.has_end_tag:
                    offset += 1
            else:
                offset -= 1
        
        if children == []:
            children = None
        
        return children
    
    
    def __repr__(self) -> str:
        
        return self.html
    
    
    def pretty_repr(self) -> str:
        
        return "IDK DO this later"
    
    
    def pretty_print(self) -> None:
        
        print(self.pretty_repr())
    
    
    def find(self, tag: str, attrs: dict = {}) -> list[Tag]:
        
        def is_in_dict(smaller, larger):
            if larger is None:
                return False
            for attr in smaller:
                try:
                    if smaller.get(attr) != larger.get(attr):
                        return False
                except KeyError:
                    return False
            return True
            
        goal_tags = []
        if attrs == {}:
            for t in self.tags:
                if t.tag == tag:
                    goal_tags.append(t)
        else:
            if tag == "":
                for t in self.tags:
                    if is_in_dict(attrs, t.attrs):
                        goal_tags.append(t)
            else:
                for t in self.tags:
                    if t.tag == tag and is_in_dict(attrs, t.attrs):
                        goal_tags.append(t)
        
        return goal_tags
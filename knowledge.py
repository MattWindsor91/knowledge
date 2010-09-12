########################################################################
#                                                                      #
# knowledge.py                                                         #
# Copyright (C) 2010 Matt Windsor                                      #
#                                                                      #
# This program is free software; you can redistribute it and/or        #
# modify it under the terms of the GNU General Public License          #
# as published by the Free Software Foundation; either version 3       #
# of the License, or (at your option) any later version.               #
#                                                                      #
# This program is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with this program; if not, see <http://www.gnu.org/licenses/>. #
#                                                                      #
########################################################################

import re

class Term (object):
    """A term, or tree node in the knowledge tree."""

    def __init__ (self, name):
        """Create the term."""
        object.__init__ (self)
        self.name = name
        self.children = []
        self.parents = []

    def add_child (self, child):
        """Add a child to this term."""
        for exchild in self.children:
            if exchild.name == child.name:
                return False

        self.children.append (child)

        return child.add_parent (self)

    def add_parent (self, parent):
        """Connect a parent to this child."""

        for exparent in self.parents:
            if exparent.name == parent.name:
                return False

        self.parents.append (parent)

        obj.prune_tree ()

        return True

    def remove_child (self, child):
        """Remove a child link."""
        if type (child) == str:
            child = obj.traverse (child)
            if child is None:
                print "FATAL: Item does not exist."
                return

        if child in self.children:
            self.children.remove (child)

    def remove_parent (self, parent):
        """Remove a parent link."""
        if type (parent) == str:
            parent = obj.traverse (parent)
            if parent is None:
                print "FATAL: Item does not exist."
                return

        if parent in self.parents:
            parent.remove_child (self)
            self.parents.remove (parent)

    def traverse (self, name):
        """Tree-search for the term object of name or alias name."""
        if name in aliases.keys ():
            name = aliases[name]

        if self.name == name:
            return self
        else:
            for child in self.children:
                val = child.traverse (name)
                if val is not None:
                    return val
            return None

    def get_name (self):
        """Retrieve this term's name."""
        return self.name

    def get_parents (self):
        """Retrieve this term's parents."""
        return self.parents

    def get_ancestry (self, alist=None):
        """Get nested lists of all the ancestors of this term."""
        if alist is None:
            alist = []
        for parent in self.parents:
            anode = [parent.get_name ()]
            anode.extend (parent.get_ancestry ())
            alist.append (anode)
        return alist

    def print_tree (self, recur_depth=0):
        """Pretty-print the tree from this node."""
        if self.name == "object":
            print "OBJECT"
        else:
            print "|" + " " * recur_depth + "\\-" + self.name

        for child in self.children:
            child.print_tree (recur_depth + 1)

    def save_tree (self, file, in_list=[]):
        """Recursively save this node's subtree into the file."""
        for parent in self.parents:
            if (self, parent) not in in_list:
                print >> file, self.name, "is a kind of", parent.get_name ()
                in_list.append ((self, parent))

        for child in self.children:
            in_list = child.save_tree (file, in_list)

        return in_list

    def prune_tree (self):
        """Walk down the tree from this point, removing all redundant 
        branches.

        This algorithm compares ancestries and breaks those which 
        are repeated in longer (more detailed) ancestries.  Therefore, 
        for example, if an object Foo has ancestries Bar->Baz->object 
        and Baz->object, the latter will be pruned as it is replicated 
        more specifically in the former.
        """

        for parent1 in self.get_ancestry ():
            for parent2 in self.get_ancestry ():
                while len (parent2) > 1:
                    if parent1 in parent2:
                        self.remove_parent (parent1[0])
                    parent2 = parent2[1]

        for child in self.children:
            child.prune_tree ()

    def update_names (self):
        """Walk down the tree from this point, replacing all aliases
        with their true names.
        """

        if self.name in aliases.keys ():
            self.name = aliases[self.name]

        for child in self.children:
            child.update_names ()

    def list_reduce (self, list=[]):
        """Reduce the tree starting from this root into a list."""
        if self not in list:
            list.append (self)

        for child in self.children:
            list = child.list_reduce (list)

        return list

obj = Term("object")
aliases = {}

def add_kind_of (x, y):
    """Create an "x is kind of y" relationship."""
    
    newobj = obj.traverse (x)

    if newobj is None:
        newobj = Term (x)

    superobj = obj.traverse (y)

    if superobj is None:
        print "WARNING: Parent object", y, "does not exist."
        print "Creating new parent object and linking to object."

        add_kind_of (y, "object")

        superobj = obj.traverse (y)

    superobj.add_child (newobj)

def is_kind_of (x, y):
    """Return whether x is a kind of y."""
    parentobj = obj.traverse (y)

    if parentobj is None:
        print "FATAL: Parent object", y, "does not exist."
    elif parentobj.traverse (x) is None:
        return False
    else:
        return True

def what_is (item, recur_depth=0):
    """Answer a "what is X?" question by printing knowledge about the 
    kind of object X is.
    """

    if type (item) == str:
        orig_item = item
        item = obj.traverse (item)
        if item is None:
            print "FATAL: Item does not exist."
            return
        elif item.get_name () != orig_item: # Alias
            print orig_item, "is an alias for", item.get_name ()

    for parent in item.get_parents():
        print " " * recur_depth + item.get_name (), \
            "is a kind of", parent.get_name() + ";"

        what_is (parent, recur_depth + 1)

def make_alias (alias, true_name):
    """Create an alias.

    Aliases map one term to another in such a way that any request for 
    the alias will immediately translate into a request for its real 
    name.

    When an alias is created, the tree will be updated to replace any 
    names matching the alias with the real name.

    TODO: ensure cyclic aliases cannot be made.
    """

    # Check to see if the true name is in itself an alias.
    item = obj.traverse (true_name)

    if item is not None:
        true_name = item.get_name ()

    if alias not in aliases.keys ():
        aliases[alias] = true_name

def save_aliases (f):
    """Save aliases to the open file."""
    for alias in aliases.keys ():
        print >> f, alias, "is an alias for", aliases[alias]

def load_aliases (f):
    """Load aliases from the open file."""
    f.seek (0)

    for line in f.readlines ():
        aa = aare.match (line)
        if aa:
            make_alias (aa.group ('alias'), aa.group ('true_name'))
            obj.update_names () 

def get_terms ():
    """Return a list of all terms the knowledge base knows about."""

    terms = [t.name for t in obj.list_reduce ()]

    for alias in aliases.keys ():
        if alias not in terms:
            terms.append (alias)

    return terms

### MAIN CODE ###

running = True

# Regexes used in command parsing.

kore = re.compile ('(?P<x>.+) is a kind of (?P<y>.+)')
wire = re.compile ('what is (?P<item>.+)\?')
aare = re.compile ('(?P<alias>.+) is an alias for (?P<true_name>.+)')

while running:
    print 
    print "Type X is a kind of Y to create a relationship."
    print "Type X is an alias for Y to create an alias."
    print "Type what is Y? to query relationships."
    print "Type quit to quit, save to save knowledge and load to load it."
    print
    print "I know about:"
    print ", ".join (get_terms ())
    print

    command = raw_input ("> ")

    km = kore.match (command)
    if km:
        add_kind_of (km.group ('x'), km.group ('y'))
        obj.print_tree ()

    aa = aare.match (command)
    if aa:
        make_alias (aa.group ('alias'), aa.group ('true_name'))
        obj.update_names ()
        obj.print_tree ()

    wi = wire.match (command)
    if wi:
        what_is (wi.group ('item'))

    if command == "quit":
        running = False
    elif command == "save":
        with open ("knowledge.db", "w") as f:
            obj.save_tree (f)
            save_aliases (f)
    elif command == "load":
        with open ("knowledge.db", "r") as f:
            for line in f.readlines ():
                km = kore.match (line)
                if km:
                    add_kind_of (km.group ('x'), km.group ('y'))
            load_aliases (f)

        obj.prune_tree ()
        obj.print_tree ()
        print aliases

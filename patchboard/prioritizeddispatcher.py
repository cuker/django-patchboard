from django.dispatch.dispatcher import Signal, _make_id, saferef

class LabeledPrioritizedSignal(Signal): #TODO make more DRY
    def __init__(self, *args, **kwargs):
        super(LabeledPrioritizedSignal, self).__init__(*args, **kwargs)
        self.receivers = RequirementsTree()

    def connect(self, receiver, label, sender=None, weak=True, dispatch_uid=None, before=[], after=[]):
        """%s
            priority
                The lower the number the sooner the handler will be called
        """ % Signal.connect.__doc__
        from django.conf import settings
        
        # If DEBUG is on, check that we got a good receiver
        if settings.DEBUG:
            import inspect
            assert callable(receiver), "Signal receivers must be callable."
            
            # Check for **kwargs
            # Not all callables are inspectable with getargspec, so we'll
            # try a couple different ways but in the end fall back on assuming
            # it is -- we don't want to prevent registration of valid but weird
            # callables.
            try:
                argspec = inspect.getargspec(receiver)
            except TypeError:
                try:
                    argspec = inspect.getargspec(receiver.__call__)
                except (TypeError, AttributeError):
                    argspec = None
            if argspec:
                assert argspec[2] is not None, \
                    "Signal receivers must accept keyword arguments (**kwargs)."
        
        if dispatch_uid:
            lookup_key = (dispatch_uid, _make_id(sender))
        else:
            lookup_key = (_make_id(receiver), _make_id(sender))

        if weak:
            receiver = saferef.safeRef(receiver, onDelete=self._remove_receiver)

        for r_key, _ in self.receivers:
            if r_key == lookup_key:
                break
        else:
            self.receivers.add((lookup_key, receiver), label, before, after)
            #self.receivers.append((lookup_key, receiver))

class RequirementsTree(object):
    class RequirementsNode(object):
        def __init__(self, tree, item, label, before, after):
            self.tree = tree
            self.item = item
            self.label = label
            self.before = before
            self.after = after
        
        def __repr__(self):
            return '<"%s", before=%s, after=%s>' % (self.label, self.before, self.after)
        
    def __init__(self):
        self.sorted_items = list()
        self.items = dict()
        self._priority_table = dict()
        # key => value, all values happen then key can happen
    
    def add(self, item, label, before=[], after=[]):
        if self.sorted_items:
            self.sorted_items = list()
        self.items[label] = self.RequirementsNode(self, item, label, before, after)
        self.before(label, before)
        self.after(label, after)
    
    def before(self, label, items):
        """
        label happens before items
        """
        for item in items:
            self.after(item, [label])
    
    def after(self, label, items):
        """
        label happens after items
        """
        self._priority_table.setdefault(label, set())
        self._priority_table[label].update(items)
        for item in items:
            if item in self._priority_table:
                self.after(label, self._priority_table[item])
        for key, value in self._priority_table.iteritems(): #if you happen after me, you also happen after these
            if label in value:
                self.after(key, items)
    
    def sort_function(self, anode, bnode):
        if anode.label in self._priority_table[bnode.label]: #a before b
            return -1
        if bnode.label in self._priority_table[anode.label]: #b before a
            return 1
        return 0
    
    def sort(self):
        items = self.items.values()
        items.sort(self.sort_function)
        self.sorted_items = items
    
    def __iter__(self):
        if not self.sorted_items and self.items:
            self.sort()
        for item in self.sorted_items:
            yield item.item
    
    def __delitem__(self, index):
        label = self.sorted_items[index].label
        del self.sorted_items[index]
        del self.items[label]


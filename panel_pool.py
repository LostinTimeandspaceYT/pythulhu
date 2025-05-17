
class PanelPool:
    def __init__(self):
        self.pool = {}  # name → panel
        self.factories = {}  # name → factory function

    def register_factory(self, name: str, factory_fn):
        self.factories[name] = factory_fn

    def get(self, name: str, *args, **kwargs):
        if name in self.pool:
            return self.pool[name]
        if name in self.factories:
            panel = self.factories[name](*args, **kwargs)
            self.pool[name] = panel
            return panel
        raise KeyError(f"No panel or factory for {name}")

    def release(self, name: str):
        panel = self.pool.pop(name, None)
        if panel:
            panel.detach_from()
            del panel
            import gc
            gc.collect()

    def clear(self):
        for name in list(self.pool.keys()):
            self.release(name)
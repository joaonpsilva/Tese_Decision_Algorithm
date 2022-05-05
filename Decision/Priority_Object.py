class Priority_Object:
    def __init__(self, object, priority, amount_kw) -> None:
        self.object = object
        self.priority = priority
        self.amount_kw = amount_kw
    
    def __repr__(self) -> str:
        return "Priority_Object: {object}, priority: {priority}, amount_kw: {amount_kw}"\
            .format(object=self.object, priority=self.priority, amount_kw=self.amount_kw)
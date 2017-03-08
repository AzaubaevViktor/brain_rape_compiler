class Base(Exception):
    fmt = "This is msg from base exception, check compiler code"

    def __init__(self, context: 'Context', **kwargs):
        self.cntx = context
        self.str = str
        self._kwargs = kwargs
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __str__(self):
        lines = []
        lines.append("Тут должен быть traceback из context")
        lines.append(self.__class__.fmt.format(**self._kwargs))
        return "\n".join(lines)

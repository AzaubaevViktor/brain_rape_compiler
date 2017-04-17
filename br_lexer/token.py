class Token:
    def __init__(self, line, pos: int, text: str):
        self.line = line
        self.pos = pos
        self.text = text

    def __repr__(self):
        return "Token<{}>".format(self.text)

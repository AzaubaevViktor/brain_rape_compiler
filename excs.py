class BrException(Exception):
    fmt_msg = ""  # type: str

    def __init__(self, place: 'Expression' or 'Token', context=None, **kwargs):
        self.place = place
        self.context = context
        self.kwargs = kwargs

    def __repr__(self):
        return repr(self.place)

    def __str__(self):
        s = ""
        s += self.fmt_msg.format(self=self, place_type=type(self.place))
        s += "\n"

        under_start = self.kwargs.get('under_start')
        under_len = self.kwargs.get('under_len')

        import br_lexer

        number_s = "{}".format(self.place.number)

        if isinstance(self.place, br_lexer.Line):
            s += "{self.place.number}: {self.place.text}\n" \
                 "{number_len}  {under_start}{under_len}".format(
                self=self,
                number_len=" " * len(number_s),
                under_start=" " * under_start,
                under_len="^" * under_len
            )

        return s

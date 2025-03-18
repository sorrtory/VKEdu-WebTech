LOREM = '''Lorem Ipsum is simply dummy text of the printing and typesetting
industry. Lorem Ipsum has been the industry's standard dummy text ever since 
the 1500s, when an unknown printer took a galley of type and scrambled it to 
make a type specimen book. It has survived not only five centuries, but also 
the leap into electronic typesetting, remaining essentially unchanged. It was 
popularised in the 1960s with the release of Letraset sheets containing Lorem 
Ipsum passages, and more recently with desktop publishing software like Aldus 
PageMaker including versions of Lorem Ipsum.'''

class CardBase:
    def __init__(self, card_type: str, header: str = None, text: str = None, tags: list = None):
        self.type = card_type   # explore / main / answer
                                # Explore cards example is on index.html
                                # Main cards example is on question.html. In fact the largest one
                                # Answer cards examples are below the main
        if header is None:
            self.header = "LOREM IPSUM"
        if text is None:
            self.text = LOREM
        if tags is None:
            self.tags = []

        # Layout
        self.AVATAR_SIZE = "2"  # col-{{AVATAR_SIZE}}
        self.CARD_BORDER = "1"  # border-{{CARD_BORDER}}


class CardFeed(CardBase):
    def __init__(self):
        super().__init__("explore")


class CardMain(CardBase):
    def __init__(self):
        super().__init__("main")
        self.AVATAR_SIZE = "3"
        self.CARD_BORDER = "0"


class CardAnswer(CardBase):
    def __init__(self):
        super().__init__("answer")

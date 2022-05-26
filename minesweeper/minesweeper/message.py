class Message(object):

    def get_representation(self):
        raise NotImplementedError()

    def __str__(self):
        return self.get_representation()


class UTSMessage(Message):
    """
    A UTSMessage (User-To-Server message) is a superclass for all those classes representing
    a message from the client to the server.
    """

    message_types = ()  # Assigned at the bottom of the file

    @staticmethod
    def parse_infer_type(raw_input):
        """
        Takes a raw_input string and returns the first concrete UTSMessage instance where raw_input
        was a valid string for static instantiation.
        :param raw_input: string to feed into a factory method.
        :return: object of a concrete UTSMessage class, or an instance of UTSInvalidMessage if the method fails
            (e.g. raw_input is "invalid").
        """
        result = None

        for i in UTSMessage.message_types:
            try:
                result = i.parse(raw_input)

                if result is not None:
                    break
            except Exception:
                continue

        if result is None:
            result = UTSInvalidMessage.parse(raw_input)

        return result

    @classmethod
    def parse(cls, raw_input):
        return cls._message_factory(raw_input.strip())

    @classmethod
    def _message_factory(cls, factory_string):
        """
        Creates an instance of a concrete UTSMessage class by using a factory method.
        :param factory_string: string to construct a new object from.
        :return: a new instance whose class is a subtype of UTSMessage.
        """
        raise NotImplementedError()

    def find_errors(self, board):
        """
        Checks the current state of this message against errors. If one is found, a string
        representation of it is returned, else None is returned.
        :param board: The shared board instance.
        :return: None if no errors were found; a human-readable string explaining the issue
                if one was found.
        """
        raise NotImplementedError()


class UTSLookMessage(UTSMessage):
    REPR = "look"

    @classmethod
    def _message_factory(cls, factory_string):
        if factory_string.endswith(UTSLookMessage.REPR, 0):
            return UTSLookMessage()
        else:
            raise ValueError("required \"%s\", found \"%s\"" %
                             (UTSLookMessage.REPR, factory_string))

    def find_errors(self, board):
        return None

    def get_representation(self):
        return self.REPR


class UTSDigMessage(UTSMessage):

    REPR_PREFIX = "dig"
    ERROR_OUT_OF_BOUNDS = "Error. The coordinates %d, %d are not contained within the board."

    def __init__(self, row, col):
        self.row = row
        self.col = col

    @classmethod
    def _message_factory(cls, factory_string):
        """
        Creates a new instance of UTSDigMessage from factory_string.
        :param factory_string: a string of the form "dig <space> [0-9]+ <space> [0-9]+". <space> refers to a single space only.
        :return: an UTSDigMessage instance created according to the method arguments.
        :raise: ValueError in case factory_string does not comply to the grammar.
        """
        components = factory_string.split(" ")
        x, y = int(components[1]), int(components[2])

        if cls.REPR_PREFIX != components[0]:
            raise ValueError("Expected %s, found %s" % (cls.REPR_PREFIX, components[0]))

        return UTSDigMessage(x, y)

    def get_representation(self):
        return "%s %d %d" % (self.REPR_PREFIX, self.row, self.col)

    def find_errors(self, board):
        if (self.row, self.col) not in board:
            return self.ERROR_OUT_OF_BOUNDS % (self.row, self.col)
        return None


class UTSFlagMessage(UTSMessage):

    REPR_PREFIX = "flag"
    ERROR_OUT_OF_BOUNDS = UTSDigMessage.ERROR_OUT_OF_BOUNDS

    def __init__(self, row, col):
        self.row = row
        self.col = col

    @classmethod
    def _message_factory(cls, factory_string):
        components = factory_string.split(" ")
        x, y = int(components[1]), int(components[2])

        if cls.REPR_PREFIX != components[0]:
            raise ValueError("Expected %s, found %s" % (cls.REPR_PREFIX, components[0]))

        return UTSFlagMessage(x, y)

    def get_representation(self):
        return "%s %d %d" % (self.REPR_PREFIX, self.row, self.col)

    find_errors = UTSDigMessage.find_errors


class UTSDeflagMessage(UTSMessage):

    REPR_PREFIX = "deflag"
    ERROR_OUT_OF_BOUNDS = UTSDigMessage.ERROR_OUT_OF_BOUNDS

    def __init__(self, row, col):
        self.row = row
        self.col = col

    @classmethod
    def _message_factory(cls, factory_string):
        components = factory_string.split(" ")
        x, y = int(components[1]), int(components[2])

        if cls.REPR_PREFIX != components[0]:
            raise ValueError("Expected %s, found %s" % (cls.REPR_PREFIX, components[0]))

        return UTSDeflagMessage(x, y)

    def get_representation(self):
        return "%s %d %d" % (self.REPR_PREFIX, self.row, self.col)

    find_errors = UTSDigMessage.find_errors


class UTSHelpRequestMessage(UTSMessage):

    REPR = "help"

    @classmethod
    def _message_factory(cls, factory_string):
        if cls.REPR == factory_string:
            return UTSHelpRequestMessage()

    def get_representation(self):
        return self.REPR

    def find_errors(self, board):
        return None


class UTSByeMessage(UTSMessage):

    REPR = "bye"

    @classmethod
    def _message_factory(cls, factory_string):
        if cls.REPR == factory_string or factory_string == "-1":
            return UTSByeMessage()
        else:
            raise ValueError("Expected %s, found %s" % (cls.REPR, factory_string))

    def get_representation(self):
        return self.REPR

    def find_errors(self, board):
        return None


# noinspection PyAbstractClass
class UTSInvalidMessage(UTSMessage):
    """
    UTSInvalidMessage represents any type of string which cannot be used to instantiate one of the other
    concrete UTSMessage classes.
    """
    STU_FACTORY = "Error. '%s' was not understood."

    def __init__(self, input):
        self.repr = input

    @classmethod
    def _message_factory(cls, factory_string):
        return UTSInvalidMessage(str(factory_string))

    def get_representation(self):
        return self.repr

    def stu_error_message_factory(self):
        return STUErrorMessage(self.STU_FACTORY % self.repr)


# noinspection PyAbstractClass
class STUMessage(Message):
    """
    A STUMessage (Server-To-User message) is the counterpart of a USTMessage, and is any kind
    of message to be sent from the server to the user.
    """
    pass


class STUBoardMessage(STUMessage):

    def __init__(self, board):
        self.board = board

    def get_representation(self):
        return str(self.board) + "\n"


class STUBoomMessage(STUMessage):

    REPR = "You hit a mine!\n"

    def get_representation(self):
        return self.REPR


class STUHelpMessage(STUMessage):

    REPR = """
*** MINESWEEPER COMMANDS HELP ***
look
\tReturns a representation of the board. No mutation occurs on the board.
dig <row> <col>
\tAttempts to dig a given square. Index errors or a dug mine are indicated automatically
\tif any of them occurs. Else a response like from a "look" message is sent.
flag <row> <col>
\tMarks a square with a flag. This command does not behave as a toggle. A second flag message
\ton the same square will not unflag it.
deflag <row> <col>
\tDeflags the indicated square, or leaves it unchanged if it was already unflagged.
help
\tDisplays this message.
bye
\tCloses the connection, ending the game for the user who submitted the message.
"""

    def get_representation(self):
        return self.REPR


class STUHelloMessage(STUMessage):

    REPR = """
Welcome to Minesweeper. %d people are playing including you.
Type 'help' for help.\n
"""

    def __init__(self, users_number):
        self.users = users_number

    def get_representation(self):
        return self.REPR % self.users


class STUErrorMessage(STUMessage):

    def __init__(self, error_msg):
        self.msg = error_msg

    def get_representation(self):
        return self.msg + "\n"


class STUByeMessage(STUMessage):

    REPR = "Quitting the game. Bye!\n"

    def get_representation(self):
        return self.REPR


UTSMessage.message_types = (UTSLookMessage, UTSDigMessage, UTSFlagMessage, UTSDeflagMessage,
                            UTSHelpRequestMessage, UTSByeMessage)
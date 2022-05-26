from enum import Enum, unique
from random import shuffle, random
from itertools import chain
from threading import RLock
from math import floor, log
from utils import digits


@unique
class State(Enum):
    UNTOUCHED = "-"
    FLAGGED = "F"
    DUG = " "

    def __init__(self, representation):
        self.representation = representation


class Square:
    REPR_BOMB = "*"

    def __init__(self, row, col, has_bomb, state):
        self.row, self.col = row, col
        self.has_bomb = has_bomb
        self.state = state

    def __repr__(self):
        return "<'%s.%s' object, row=%d, col=%d, has_bomb=%s, state=%s>" % \
               (self.__class__.__module__, self.__class__.__name__, self.row, self.col,
                self.has_bomb, self.state.name)

    def __str__(self):
        if self.state == State.DUG and self.has_bomb:
            return Square.REPR_BOMB
        return self.state.representation


class Board:
    """ Problem 3, point b. Thread safety argument:\n
    Thread safety is currently ensured in Board only. The Square class and any other lack
    any type of coverage. Accessing some of the Board's squares through the Square class can lead to race conditions.
    Board is made thread-safe exclusively by synchronization, by using a reentrant lock (a RLock). The self._squares
    attribute, which can nevertheless be accessed even though it is marked private (Python does not provide access
    protection), can be legitimately accessed and modified by observer and mutator methods. These all use
    synchronization, and as long as a client of Board does not attempt a direct access at self._squares or at an
    instance of Square, race conditions should not occur. (Of course a rewriting of the Square class may be operated,
    for ensuring better security. This, however, is not being done for lack of time.) I do not see any piece of
    code using techniques such as thread confinement, immutability or threadsafe datatypes for ensuring thread
    security on this class. (Thread safety techniques discussed in the lecture notes of this course are, indeed,
    confinement, immutability, thread safe datatypes and synchronization.)
    Besides arguments for the thread-safety of Board, a test to confirm that no race conditions occur inside Board is
    included in board_test.py.
    """
    # Height, width, mines_count number
    DIFF_EASY = (9, 9, 10)
    DIFF_INTERMEDIATE = (16, 16, 40)
    DIFF_HARD = (16, 30, 99)

    def __init__(self, boolean_grid):
        self._squares = list()
        self._lock: RLock = RLock()

        self._lock.acquire()

        for row in range(len(boolean_grid)):
            self._squares.append(list())

            for col in range(len(boolean_grid[row])):
                self._squares[row].append(
                    Square(row, col, boolean_grid[row][col], State.UNTOUCHED)
                )

        self._check_state()
        self._lock.release()

    @staticmethod
    def create_from_probability(height, width, bomb_probability=0.25):
        """
        Create a new board by supplying a **height**, a **width** and a bomb probability parameters.
        :param height: number of rows of the board, each with an even number of elements.
        :param width: number of elements for each row.
        :param bomb_probability: the probability that a cell of the grid has a bomb during creation.
            **bomb_probability** must belong to [0, 1).
        :return: a new Board instance.
        """
        if height * width <= 0:
            raise ValueError("The grid size must be greater than 0 (found %d)" % height * width)
        if not 0 <= bomb_probability < 1:
            raise ValueError("It must be 0 <= bomb_probability <= 1 (bomb_probability = %f)" % bomb_probability)

        squares = list()

        for square in range(height * width):
            squares.append(random() <= bomb_probability)

        return Board(Board._list_to_grid(squares, height, width))

    @staticmethod
    def create_from_difficulty(difficulty=DIFF_EASY):
        """
        Create a new board by supplying a pre-made or a custom difficulty level.
        :param difficulty: a (**height**, **width**, **mines**) tuple.
        :return: a Board instance with **height** rows, each **width**-elements wide, containing
            **mines** mines randomly interspersed in its grid.
        """
        height, width, mines = difficulty

        if height * width <= 0:
            raise ValueError("The grid size must be greater than 0 (found %d)" % height * width)
        if not 0 < mines < height * width:
            raise ValueError("0 < mines < %d not true (mines = %d)" % (height * width, mines))

        squares = Board._random_mines_distribution((height * width) - mines, mines)

        return Board(Board._list_to_grid(squares, height, width))

    @staticmethod
    def create_from_file(path):
        """
        Create a new board as instructed in Problem 4 of the assignment.
        :param path: a string representing a file containing a well-formatted grid of 0s and 1s.
        :return: a new Board instance.
        """

        def read_line(text_line):
            sep = " "
            encoding = {'0': False, '1': True}

            # dict.get() returns None when a given argument is not contained within the dict keys
            line = [encoding.get(i) for i in text_line.strip().split(sep)]

            if None in line:
                raise ValueError("Found invalid content in '%s'. Every line can contain only 0s and 1s" % path)

            return line

        with open(path) as f:
            lines = [read_line(line) for line in f]

            for line in lines:
                if len(line) != len(lines):
                    raise ValueError("Found %d wide line in a %d tall grid, square grid expected" %
                                     (len(line), len(lines)))

        return Board(lines)

    def __repr__(self):
        with self._lock:
            return "<'%s.%s' object, height=%d, width=%d, mines_count=%d>" % \
                   (self.__class__.__module__, self.__class__.__name__, self.height(), self.width(), self.mines_count())

    def __str__(self):

        def format_row(row):
            result = ""

            for square in row:
                if square.state in (State.UNTOUCHED, State.FLAGGED):
                    result += "%s " % str(square)
                elif square.state == State.DUG:
                    if square.has_bomb:
                        result += "%s " % str(square)
                    else:
                        nearby_bombs = len([n for n in self.neighbors(square.row, square.col) if n.has_bomb])

                        if nearby_bombs == 0:
                            result += str(square) + " "
                        else:
                            result += "%d " % nearby_bombs

            return result

        def format_row_header():
            """
            :return: A header line to be displayed on top of the board grid.
            """
            sep = " "
            hmaxdigits = digits(self.width())               # The maximum number of digits that a column index can take
            vpad = sep * (digits(self.height() - 1) + 1)    # The vertical padding whitespace to add before this header
            # The column indices, in string form, padded with the required whitespace
            indices = [(str(i).ljust(hmaxdigits))[::-1] for i in range(self.width())]
            result = ""

            for i in range(hmaxdigits):
                # result is added a new header line at each iteration
                result += vpad + sep.join([index[i] for index in indices])

                if i < hmaxdigits - 1:
                    result += "\n"

            return result

        def vertical_padding(rowindex):
            """
            :param rowindex: index of the board row being displayed
            :return: the padding to be appended in front of a board row to allow proper alignment
            """
            return " " * (digits(self.height() - 1) + 1 - digits(rowindex))

        result = format_row_header() + "\n"

        self._lock.acquire()

        for rowindex, row in zip(range(self.height()), self._squares):
            result += str(rowindex) + vertical_padding(rowindex) + format_row(row) + "\n"

        self._lock.release()

        return result

    def __len__(self):
        with self._lock:
            return sum([len(row) for row in self._squares])

    def __contains__(self, key):
        if not (isinstance(key[0], int) and isinstance(key[1], int)):
            raise ValueError("Arguments must be integers (found %s, %s)" % (key[0], key[1]))

        with self._lock:
            return 0 <= key[0] < len(self._squares) and \
                   0 <= key[1] < len(self._squares[key[0]])

    def __iter__(self):
        with self._lock:
            return iter(chain(*self._squares))

    def square(self, row, col):
        with self._lock:
            return self._squares[row][col]

    def height(self):
        with self._lock:
            return len(self._squares)

    def width(self):
        with self._lock:
            return len(self._squares[0]) if len(self._squares) > 0 else 0

    def mines_count(self):
        """
        :return: an int indicating the number of squares where has_bomb evaluates to true, i.e. those squares
            which have a bomb, or are "mined".
        """
        with self._lock:
            return len([square for square in self if square.has_bomb])

    def set_state(self, row, col, state):
        """
        Set the state of a square indicated by (row, col) to state.
        If state is DUG and the current square has no bomb, then its adjacent squares
        are all dug if none of them has a bomb.
        :param row: row coordinate
        :param col: col coordinate
        :param state: State value to set the (row, col) square into
        """
        self._lock.acquire()

        if (row, col) not in self:
            raise ValueError("%d, %d coordinates are out of range" % (row, col))

        self._squares[row][col].state = state

        if state == State.DUG and not self._squares[row][col].has_bomb:
            neighbors = self.neighbors(row, col)
            nearby_bombs = len([n for n in neighbors if n.has_bomb])

            if nearby_bombs == 0:
                for n in [s for s in neighbors if s.state != State.DUG]:
                    self.set_state(n.row, n.col, State.DUG)

        self._lock.release()

    def neighbors(self, row, col):
        """
        :return: a list containing all those squares which are one square away from the (row, col) square, that is its
            "neighbours".
        """
        self._lock.acquire()

        result = list()
        min_row, max_row = max(row - 1, 0), min(row + 1, len(self._squares) - 1)
        min_col, max_col = max(col - 1, 0), min(col + 1, len(self._squares[row]) - 1)

        for x in range(min_row, max_row + 1):
            for y in range(min_col, max_col + 1):
                if (x, y) != (row, col):
                    result.append(self._squares[x][y])

        self._lock.release()

        return result

    def _check_state(self):
        """
        Performs validity checks on the current instance, raising relevant exceptions when detecting an invalid state.
        :return: True if no inconsistencies were found within the current instance.
        """
        self._lock.acquire()
        expected_line_length = len(self._squares[0]) if len(self._squares) > 0 else None

        for line in self._squares:
            types = {type(square) for square in line}

            if {Square} != types:
                raise ValueError("The board can only contain Square variables within its grid")
            if len(line) != expected_line_length:
                raise ValueError("Found a %d-element-wide line, expected %d" % (len(line), expected_line_length))

        self._lock.release()

        return True

    @staticmethod
    def _random_mines_distribution(empty_squares, mined_squares):
        distribution = [False for i in range(empty_squares)]
        distribution.extend([True for i in range(mined_squares)])
        shuffle(distribution)

        return distribution

    @staticmethod
    def _list_to_grid(squares, height, width):
        """
        Utility method used to convert a flat list of boolean values (representing mined squares) to
        a multi-dimensional list with specified height and width.
        :param squares: one-dimensional list of squares.
        :param height: height of the resulting grid.
        :param width: number of elements for each of the **height** rows.
        :return: a grid-like list with the same values as **squares**.
        """
        return [squares[i * width:(i * width) + width] for i in range(height)]

    def toggle_dug(self, toggles=1):
        """
        Switches the state of every square contained in this board between UNTOUCHED and DUG (see the code
        for more info). If the state of a square is FLAGGED no modification occurs.\n
        This method is primarily used for debug purposes.
        """
        self._lock.acquire()

        for i in range(toggles):
            for s in self:
                if s.state == State.UNTOUCHED:
                    # self.set_state(s.row, s.col, State.DUG)
                    s.state = State.DUG
                elif s.state == State.DUG:
                    # self.set_state(s.row, s.col, State.UNTOUCHED)
                    s.state = State.UNTOUCHED

        self._lock.release()
from board import Board


def do_experiment():
    n = list(range(1, 11))
    print(" | ".join([str(i) for i in n]))


def do_string_experiment():
    s = "*" * 5
    print(s)


def do_board_experiment():
    b = Board.create_from_probability(15, 15, 0.25)
    print(b)

if __name__ == "__main__":
    do_board_experiment()
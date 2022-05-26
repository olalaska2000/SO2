import concurrent.futures
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from logging import *
from socket import *
from sys import argv, stdout
from time import sleep

from board import Board, State
from message import *
from utils import is_boolean


class MineSweeperServer:

    DEFAULT_CONFIGS = {
        "host": '',
        "port": 8080,
        "listen_backlog": 0,
        "max_clients": 4
    }

    def __init__(self, board, port=DEFAULT_CONFIGS["port"], debug=False):
        self._board = board
        self._futures_to_connections = dict()
        self.max_clients = self.DEFAULT_CONFIGS["max_clients"]

        self._server = socket(AF_INET, SOCK_STREAM)
        self._server.bind((self.DEFAULT_CONFIGS["host"], port))
        self._server.listen(self.max_clients)

        self._executor = ThreadPoolExecutor(self.max_clients + 1)

        self.is_closed = False


        self._logger = getLogger(__name__)
        self._logger.setLevel(DEBUG)
        self._logger.addHandler(StreamHandler(stdout) if debug else NullHandler())

        self._logger.debug("Listening at port %d...", port)

    def __repr__(self):
        repr_unknown = "unknown"

        if not self.is_closed:
            host = self._server.getsockname()[0] or repr_unknown
            port = self._server.getsockname()[1] or repr_unknown
        else:
            host = port = repr_unknown

        return "<'%s.%s' object, host=%s, port=%s, debug=%s>" %\
               (MineSweeperServer.__module__, self.__class__.__name__, host, port, self.is_debug_enabled())

    def __del__(self):
        if not self.is_closed:
            self.close()

    def close(self):
        if not self.is_closed:
            self._executor.shutdown(False)

            self._server.shutdown(SHUT_RDWR)
            self._server.close()
            del self._server

            self.is_closed = True

            self._logger.debug("%s was closed" % repr(self))

    def futures(self):
        return self._futures_to_connections.keys()

    def connections(self):
        return self._futures_to_connections.values()

    def next_connection(self):
        if self.is_full():
            self._logger.debug(
                "Reached maximum number of connections: %d/%d occupied",
                len(self._futures_to_connections), self.max_clients
            )
            return None
        else:
            connection = Connection(
                self,
                self._server.accept()[0],
                self.is_debug_enabled()
            )
            future = self._executor.submit(connection)
            future.add_done_callback(self._make_callback_shutdown_client())

            self._futures_to_connections[future] = connection

            return future

    def is_full(self):
        return len(self._futures_to_connections) >= self.max_clients

    def is_debug_enabled(self):
        return NullHandler not in (type(h) for h in self._logger.handlers)

    def _make_callback_shutdown_client(self):

        def _callback_shutdown_client(future):
            connection = self._futures_to_connections[future]

            connection.close()
            self._futures_to_connections.pop(future)

            self._logger.debug(
                "Connection closed: %d/%d still running",
                len(self._futures_to_connections),
                self.max_clients
            )

        return _callback_shutdown_client


class Connection:

    def __init__(self, ms_server: MineSweeperServer, client: socket, debug=False):
        self.server = ms_server
        self.board = self.server._board
        self.client: socket = client

        self.is_closed = False
        self.logger = getLogger(__name__)

    def __repr__(self):
        return repr(self.client)

    def __del__(self):
        if not self.is_closed:
            self.close()

    def __call__(self, *args, **kwargs):
        return self.run()

    def run(self):
        self.logger.debug("%s:%s connected", *self.client.getpeername())

        # TO-DO Could the line of code below be subject to a race condition?
        connections = len(self.server.connections())
        if self not in self.server.connections():
            connections += 1

        self.client.send(
            STUHelloMessage(connections).get_representation().encode()
        )

        # TO-DO Verify open() is being used correctly
        with open(self.client.fileno()) as stream:
            in_message = UTSMessage.parse_infer_type(stream.readline())

            while in_message is not None:
                self.logger.debug("%s:%s: %s", *self.client.getpeername(), in_message)

                out_message = self._process_in_message(in_message)
                self.client.send(out_message.get_representation().encode())

                if isinstance(out_message, STUBoomMessage):
                    in_message = None
                elif isinstance(out_message, STUByeMessage):
                    in_message = None
                else:
                    in_message = UTSMessage.parse_infer_type(stream.readline())

    def close(self):
        if not self.is_closed:
            addrinfo = str(self.client)

            if self.client is not None:
                try:
                    self.client.close()
                    self.client.shutdown(SHUT_RDWR)
                except OSError:
                    pass

            self.is_closed = True

            self.logger.debug("'%s' closed", addrinfo)

    def is_debug_enabled(self):
        return NullHandler not in (type(h) for h in self.logger.handlers)

    def _process_in_message(self, in_message):
        result = None

        if isinstance(in_message, UTSLookMessage):
            result = STUBoardMessage(self.board)
        elif isinstance(in_message, UTSDigMessage):
            error = in_message.find_errors(self.board)

            if error is None:
                self.board.set_state(in_message.row, in_message.col, State.DUG)
                square = self.board.square(in_message.row, in_message.col)

                if square.has_bomb:
                    square.has_bomb = False
                    result = STUBoomMessage()
                else:
                    result = STUBoardMessage(self.board)
            else:
                result = STUErrorMessage(error)
        elif isinstance(in_message, UTSFlagMessage):
            error = in_message.find_errors(self.board)

            if error is None:
                self.board.set_state(in_message.row, in_message.col, State.FLAGGED)

                result = STUBoardMessage(self.board)
            else:
                result = STUErrorMessage(error)
        elif isinstance(in_message, UTSDeflagMessage):
            error = in_message.find_errors(self.board)

            if error is None:
                square = self.board.square(in_message.row, in_message.col)

                if square.state == State.FLAGGED:
                    self.board.set_state(in_message.row, in_message.col, State.UNTOUCHED)

                result = STUBoardMessage(self.board)
            else:
                result = STUErrorMessage(error)
        elif isinstance(in_message, UTSHelpRequestMessage):
            result = STUHelpMessage()
        elif isinstance(in_message, UTSByeMessage):
            result = STUByeMessage()
        elif isinstance(in_message, UTSInvalidMessage):
            result = in_message.stu_error_message_factory()

        return result


def main():
    configs = {
        "size": 10,
        "port": MineSweeperServer.DEFAULT_CONFIGS["port"],
        "program_name": "Minesweeper server",
        "bomb_probability": 0.20,
        "sleep": 2,
    }
    logger = getLogger(__name__)
    ap = ArgumentParser(configs["program_name"])

    ap.add_argument("-d", "--debug", dest="debug", action="store", type=is_boolean,
                    required=True, help="Debug flag for server")
    ap.add_argument("-p", "--port", dest="port", action="store", type=int,
                    default=configs["port"], help="Local port where to bind the server")

    creation_group = ap.add_mutually_exclusive_group()
    creation_group.add_argument("-s", "--size", dest="size", action="store", type=int,
                                help="Value of the height and width of the grid")
    creation_group.add_argument("-f", "--file", dest="file", action="store", type=str,
                                help="Path pointing to a board file")

    arguments = ap.parse_args(argv[1:])

    if arguments.size is not None:
        board = Board.create_from_probability(
            arguments.size,
            arguments.size,
            configs["bomb_probability"]
        )
    elif arguments.file is not None:
        board = Board.create_from_file(arguments.file)
    else:
        board = Board.create_from_probability(configs["size"], configs["size"])

    server = MineSweeperServer(board, arguments.port, arguments.debug)

    while True:
        try:
            if server.is_full():
                logger.debug(
                    "Server full (%d/%d connections occupied). Waiting for older ones to be freed...",
                    len(server.connections()),
                    server.max_clients
                )
                concurrent.futures.wait(server.futures(), None, concurrent.futures.FIRST_COMPLETED)
                sleep(configs["sleep"])
            else:
                server.next_connection()
        except KeyboardInterrupt:
            break

    server.close()

if __name__ == "__main__":
    main()
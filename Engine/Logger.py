class Logger:

    console = None

    @classmethod
    def connect_console(cls, console):

        cls.console = console

    @classmethod
    def info(cls, message):

        print(message)

        if cls.console is not None:

            cls.console.log(message)
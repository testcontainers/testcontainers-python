import progressbar


class ConsoleProgressBar(object):
    def __init__(self):
        self.bar = progressbar.ProgressBar(widgets=[
            'Waiting for container to be ready: ',
            ' [', progressbar.Timer(), '] ',
        ], max_value=progressbar.UnknownLength)

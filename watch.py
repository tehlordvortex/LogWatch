from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os


class WatchHandler(FileSystemEventHandler):

    def __init__(self, queue, path, callback):
        super().__init__()
        self.path = path
        self.queue = queue
        self.callback = callback

    def on_modified(self, event):
        if event.src_path == self.path:
            self.queue.put((self.callback, event))


class Watch(object):

    def __init__(self, queue, path, callback):
        self.path = path
        self.queue = queue
        self.callback = callback
        self.handler = WatchHandler(queue, path, callback)
        self.observer = Observer()
        self.watch = self.observer.schedule(
            self.handler,
            os.path.dirname(path),
            recursive=False)

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()

    def updatePath(self, path):
        self.path = path
        self.handler = WatchHandler(self.path, self.callback)
        self.observer.unschedule(self.watch)
        self.watch = self.observer.schedule(
            self.handler,
            os.path.dirname(self.path),
            recursive=False)

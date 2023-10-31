from events import Events


def something_changed(reason):
    print("Something changed because %s" % reason)


events = Events()

events.on_change += something_changed

events.on_change("it had to happen")

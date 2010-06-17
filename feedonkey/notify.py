from feedonkey.logger import log

def show_notification_msg(title, msg):
    """show a notification message"""
    try:
        import pynotify
        if pynotify.init("Feed Donkey"):
            n = pynotify.Notification(title, msg, 'stock_view-details')
            n.show()
    except Exception, e:
        log.warn('pynotify is not installed on this machine, notification off')


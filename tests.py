#coding=UTF-8
from feedonkey import core
from feedonkey import ed2klink
from datetime import datetime

class DebugFeedMgr(object):
    """Mock feed manager for debugging"""

    def read_feeds(self):
        """docstring for read_feeds"""
        update_time = datetime(2010, 6, 1, 12, 50, 10)
        return ( [('http://www.verycd.com/topics/2752686/feed', '.*\.rmvb', update_time)],
                {'http://www.verycd.com/topics/2752686/feed': update_time}
                )

    def write_histories(self, histories):
        print histories


class DebugLinkHanler(object):
    """Simple link handler that only prints the links, for debugging"""

    def __init__(self):
        self.name='Debug'

    def handle_ed2k_links(self, links):
        """print all the ed2k links"""
        print  '\n-------------\n'.join(links)
        return True


def test_feed_observer():
    handler = DebugLinkHanler()
    test_observer = core.VeryCDFeedDownloader(handler, feed_mgr=DebugFeedMgr())
    test_observer.run_once()

def test_notify():
    from feedonkey import notify
    notify.show_notification_msg('开始下载', '[钢之炼金术师].[jumpcn][FULLMETAL.ALCHEMIST][61][848x480].rmvb')

if __name__ == "__main__":
    test_feed_observer()
    #test_notify()

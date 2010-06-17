#coding=UTF-8

def test_feed_observer():
    from feedonkey import core
    from feedonkey import ed2klink
    handler = ed2klink.PrintLinkHanler()
    test_observer = core.FeedObserver('http://www.verycd.com/topics/2752686/feed', handler, filter='.*\.rmvb')
    test_observer.check_feed()

def test_notify():
    from feedonkey import notify
    notify.show_notification_msg('开始下载', '[钢之炼金术师].[jumpcn][FULLMETAL.ALCHEMIST][61][848x480].rmvb')

if __name__ == "__main__":
    #test_feed_observer()
    test_notify()

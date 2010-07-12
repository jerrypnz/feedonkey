#coding=UTF-8
import feedparser
import re
import os.path
import time
from datetime import datetime

from feedonkey.utils import line_token_iterator
from feedonkey.config import CONFIG_DIR
from feedonkey.logger import log
from feedonkey import notify

#--- Constants ----------------------------------------------
INTERNAL_DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'
FEED_LIST_FILE = os.path.join(CONFIG_DIR, "feeds.list")
HISTORY_FILE = os.path.join(CONFIG_DIR, "histories.conf")

#--- Classes ----------------------------------------------

class FeedObserver(object):

    """VeryCD feed downloader"""
    def __init__(self, url, filter='.*', last_update_time=None):
        self.url = url
        self.filter_reg = re.compile(filter)
        self.last_update_time = last_update_time
        self.current_latest_time = last_update_time


    def __is_new(self, item_date_tup):
        """compare the date in an rss item with last update time of this feed"""
        item_time = time.mktime(item_date_tup)
        if self.last_update_time == None or item_time > self.last_update_time:
            if self.current_latest_time == None or item_time > self.current_latest_time:
                self.current_latest_time = item_time
            return True
        else:
            return False


    def check_updates(self):
        """extract a list of file info from a given verycd feed URL"""
        feed = feedparser.parse(self.url)
        return [
                item.description.encode('UTF-8')
                for item in feed.entries
                if re.match(self.filter_reg, item.title)
                    and self.__is_new(item.date_parsed)
               ]



class FeedConfigFileMgr(object):
    """feed reader"""

    def read_feeds(self):
        """read the feeds and their latest update time"""
        if not os.path.exists(FEED_LIST_FILE):
            log.warn("feeds.list not found")
            return ([], None)

        histories = {}
        if os.path.exists(HISTORY_FILE):
            for parts in line_token_iterator(HISTORY_FILE):
                histories[parts[0]] = float(parts[1])

        feeds = []
        for parts in line_token_iterator(FEED_LIST_FILE, support_comment=True):
            total_parts = len(parts)
            url = parts[0]
            filter = total_parts > 1 and parts[1] or '.*'

            try:
                last_update_time = histories[url]
            except KeyError, e:
                last_update_time = None
                pass

            if last_update_time == None and total_parts > 2:
                try:
                    tmp_time_struct = datetime.strptime(parts[2], INTERNAL_DATE_FORMAT).timetuple()
                    last_update_time = time.mktime(tmp_time_struct)
                except ValueError, e:
                    log.error('invalid date: %s' % parts[2], e)
                    pass
            log.debug("feed[url=%s, filter=%s, last_update_time=%s]" % (url, filter, last_update_time))
            feeds.append((url, filter, last_update_time))

        return (feeds, histories)



    def write_histories(self, histories):
        """write the histories to the histories.conf"""
        his_file = file(HISTORY_FILE, 'w')
        for url, last_update_time in histories.items():
            if last_update_time != None:
                his_file.write("%s %f \n" %(url, last_update_time))
        his_file.close()



class VeryCDFeedDownloader(object):
    """Main class for this script. It reads configuration file and create observers and call them to check feed updates"""
    def __init__(self, handler, interval=600, feed_mgr=FeedConfigFileMgr()):
        self.interval = interval
        self.ed2k_handler = handler
        self.feed_mgr = feed_mgr


    def run_daemon(self):
        """main flow of the script."""
        while (True):
            self.run_once()
            time.sleep(self.interval)


    def run_once(self):
        """
            read the actual file instead of caching the feed info,
            so that the modification to the feeds.list
            could be read without restarting the daemon
        """
        feeds, histories = self.feed_mgr.read_feeds()
        log.debug("loading feeds and their last update time")

        if len(feeds) != 0 :
            observers = [ FeedObserver(url, filter=file_filter, last_update_time=last_update_time)
                          for url, file_filter, last_update_time in feeds]

            log.debug("checking for updates")
            updated = False
            for observer in observers:
                links = observer.check_updates()
                if len(links) > 0:
                    if self.ed2k_handler.handle_ed2k_links(links):
                        notify.show_notification_msg("VeryCD Feed已更新", "%s已更新，成功添加%d新文件至%s"
                                % (observer.url, len(links), self.ed2k_handler.name) )
                    histories[observer.url] = observer.current_latest_time
                    updated = True

            if updated:
                self.feed_mgr.write_histories(histories)

            log.debug("finished checking")
        else :
            log.debug("no feeds found")



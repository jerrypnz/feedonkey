import feedparser
import re
import os.path
import time
from datetime import datetime

from feedonkey.utils import line_token_iterator
from feedonkey.config import CONFIG_DIR
from feedonkey.logger import log
from feedonkey import ed2klink

#--- Constants ----------------------------------------------
_RSS_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S'
_INTERNAL_DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'

#--- Classes ----------------------------------------------

class FeedObserver(object):

    """VeryCD feed downloader"""
    def __init__(self, url, handler, filter='.*', last_update_time=None):
        self.url = url
        self.handler = handler
        self.filter_reg = re.compile(filter)
        self.last_update_time = last_update_time
        self.current_latest_time = last_update_time


    def check_feed(self):
        """process VeryCD feed updates"""
        links = self.__extract_file_info()
        self.handler.handle_ed2k_links(links)
        return (self.url, self.current_latest_time)


    def __is_new(self, item_date_s):
        """compare the date in an rss item with last update time of this feed"""
        item_date = datetime.strptime(item_date_s.replace(' +0000',''), _RSS_DATE_FORMAT)
        if self.last_update_time == None or item_date > self.last_update_time:
            if self.current_latest_time == None or item_date > self.current_latest_time:
                self.current_latest_time = item_date
            return True
        else:
            return False


    def __extract_file_info(self):
        """extract a list of file info from a given verycd feed URL"""
        feed = feedparser.parse(self.url)
        items = feed['items']
        return [
                item['description'].encode('UTF-8')
                for item in items
                if re.match(self.filter_reg, item['title'])
                    and self.__is_new(item['date'].encode('UTF-8'))
               ]




class VeryCDFeedDownloader(object):
    """Main class for this script. It reads configuration file and create observers and call them to check feed updates"""
    def __init__(self, interval=600):
        self.interval = interval
        self.ed2k_handler = ed2klink.MLDonkeyLinkHandler()
        self.feed_list_file = os.path.join(CONFIG_DIR, "feeds.list")
        self.histories_file = os.path.join(CONFIG_DIR, "histories.conf")


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
        feeds, histories = self.__read_feeds()
        log.debug("loading feeds and their last update time")

        if len(feeds) != 0 :
            observers = [ FeedObserver(url, self.ed2k_handler, filter=file_filter, last_update_time=last_update_time)
                          for url, file_filter, last_update_time in feeds]

            log.debug("checking for updates")
            for observer in observers:
                url, latest_time = observer.check_feed()
                histories[url] = latest_time

            self.__write_histories(histories)

            log.debug("finished checking")
        else :
            log.debug("no feeds found")




    def __read_feeds(self):
        """read the feeds and their latest update time"""
        if not os.path.exists(self.feed_list_file):
            log.warn("feeds.list not found")
            return ([], None)

        histories = {}
        if os.path.exists(self.histories_file):
            for parts in line_token_iterator(self.histories_file):
                histories[parts[0]] = datetime.strptime(parts[1], _INTERNAL_DATE_FORMAT)

        feeds = []
        for parts in line_token_iterator(self.feed_list_file, support_comment=True):
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
                    last_update_time = datetime.strptime(parts[2], _INTERNAL_DATE_FORMAT)
                except ValueError, e:
                    log.error('invalid date: %s' % parts[2], e)
                    pass
            log.debug("feed[url=%s, filter=%s, last_update_time=%s]" % (url, filter, last_update_time))
            feeds.append((url, filter, last_update_time))

        return (feeds, histories)



    def __write_histories(self, histories):
        """write the histories to the histories.conf"""
        his_file = file(self.histories_file, 'w')
        for url, last_update_time in histories.items():
            if last_update_time != None:
                his_file.write("%s %s \n" %(url, datetime.strftime(last_update_time, _INTERNAL_DATE_FORMAT)))
        his_file.close()


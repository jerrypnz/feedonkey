import telnetlib

from feedonkey.logger import log

class MLDonkeyLinkHandler(object):
    """MLDonkey link handler, which submits ed2k download links"""
    def __init__(self, host='127.0.0.1', port=4000):
        self.host = host
        self.port = port


    def handle_ed2k_links(self, links):
        """submit ed2k links to MlDonkey"""
        tn = telnetlib.Telnet(self.host, self.port, 10)
        # > is the command indicator of MLDonkey
        tn.read_until('>')
        for link in links:
            self.__send_command(tn, 'dllink %s' % link)
        self.__send_command(tn, 'exit')
        ml_output = tn.read_all()
        log.info('MLDonkey telnet outputs'
                + '\n---------------------------------------------\n'
                + ml_output
                + '\n---------------------------------------------\n')
        tn.close()


    def __send_command(self, telnet, command):
        """send a command to the given telnet"""
        log.info('sending command \'%s\' to MLDonkey' % command)
        telnet.write('%s\n' % command)


class PrintLinkHanler(object):
    """Simple link handler that only prints the links, for debugging"""

    def handle_ed2k_links(self, links):
        """print all the ed2k links"""
        print '\n-------------\n'.join(links)



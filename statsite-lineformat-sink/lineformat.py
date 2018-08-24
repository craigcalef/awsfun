"""
Supports flushing statsite metrics to a Line Protocol sink (such as Influx)

/etc/statsite/sinks/lineformat.sh: 
"""
import sys
import collections
import httplib
import urllib
import logging
import re
import json
import socket

##
# Line Format sink for Statsite
# ==========================
#
# Use with the following stream command:
#
#  stream_command = python sinks/lineformat.py lineformat.ini INFO
#
# Or in '/etc/statsite/sinks/lineformat.sh':
#  cut -d"." -f3- | python
#    /etc/statsite/sinks/lineformat.py /etc/statsite/lineformat.ini ERROR >>
#    /var/log/statsite-sink-lineformat.log 2>&1
#
# The Lineformat sink takes an INI format configuration file as a first
# argument and log level as a second argument.
# The following is an example configuration:
#
# Configuration example "lineformat.ini":
# ---------------------
#
#[lineformat]
#host = 127.0.0.1
#port = 8089
#database = FOO
#username = change
#password = me
#timeout = 10
#
# Options:
# --------
#  - timeout:  The timeout blocking operations (like connection attempts)
#              will timeout after that many seconds (if it is not given, the global default timeout setting is used)
###

class Lineformat(object):
    def __init__(self, cfg="/etc/statsite/lineformat.ini", lvl="INFO"):
        """
        Implements an interface that allows metrics to be persisted to a sink that accepts the Line Format protocol

        Raises a :class:`ValueError` on bad arguments or `Exception` on missing
        configuration section.

        :Parameters:
            - `cfg`: INI configuration file.
            - `lvl`: logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """

        self.sink_name = "statsite-lineformat"
        self.sink_version = "0.1"

        self.logger = logging.getLogger("statsite.lineformat")
        self.logger.setLevel(lvl)

        self.loadcfg(cfg)
        self.suffix_re = re.compile("(.+)\.(sum|sum_sq|count|stdev|lower|upper|mean|p99)$")
	self.metrics = collections.defaultdict(dict)


    def loadcfg(self, cfg):
        """
        Loads configuration from an INI format file.
        """
        import ConfigParser
        ini = ConfigParser.RawConfigParser()
        ini.read(cfg)

        sect = "lineformat"
        if not ini.has_section(sect):
            raise Exception("Can not locate config section '" + sect + "'")

        if ini.has_option(sect, 'host'):
            self.host = ini.get(sect, 'host')
        else:
            raise ValueError("host must be set in config")

        if ini.has_option(sect, 'port'):
            self.port = int(ini.get(sect, 'port'))
        else:
            raise ValueError("port must be set in config")

        #if ini.has_option(sect, 'database'):
        #    self.database = ini.get(sect, 'database')
        #else:
        #    raise ValueError("database must be set in config")

        #if ini.has_option(sect, 'username'):
        #    self.username = ini.get(sect, 'username')
        #else:
        #    raise ValueError("username must be set in config")

        #if ini.has_option(sect, 'password'):
        #    self.password = ini.get(sect, 'password')
        #else:
        #    raise ValueError("password must be set in config")

        self.prefix = None
        if ini.has_option(sect, 'prefix'):
            self.prefix = ini.get(sect, 'prefix')

        self.timeout = None
        if ini.has_option(sect, 'timeout'):
            self.timeout = float(ini.get(sect, 'timeout'))

    def readmetrics(self, rawmetrics):
        for rm in rawmetrics:
            key, value, ts = rm.split('|')
            sfx_match = self.suffix_re.match(key)
            if sfx_match != None:
                key = sfx_match.group(1)
                field = sfx_match.group(2)
            else:
                field = 'value'
            self.metrics[key]['ts'] = ts
            self.metrics[key][field] = value

    def derivetags(self, mkey):
        return {}

    def flush(self):
        """
        Flushes the metrics provided to InfluxDB.

        Parameters:
        - `metrics` : A list of (key,value,timestamp) tuples.
        """
        if not self.metrics:
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.timeout:
            sock.settimeout(self.timeout)

        for mk, m in self.metrics.items():
            if 'ts' not in m:
                continue
            ts = m.pop('ts')
            fields = ",".join(["{}={}".format(k,v) for k,v in m.items()])

            tags = self.derivetags(mk)

            if "#" in mk:
                mk, explicit_tags_raw = mk.split("#")
                explicit_tags = dict(et.split('=') for et in explicit_tags_raw.split(','))
                # Explicit tags take preference
                tags.update(explicit_tags)

            for k,v in tags.items():
                if v == '' or v==' ' or not v:
                    tags.pop(k)

            if tags:
                outmetric = "{},{}".format(mk, ",".join(["{}={}".format(k,v) for k,v in tags.items()])).replace(' ', '_')
            else:
                outmetric = mk

            # The nine 0's is because Influx wants time in nanoseconds
            mv = "{} {} {}000000000".format(outmetric, fields, ts)
            self.logger.debug("Emitting measurement: {}".format(mv))
            self.logger.debug("Sending UDP packet to {}:{}".format(self.host,
                self.port))
            sock.sendto(mv+"\n", (self.host, self.port))

        sock.close()
        self.logger.info("Flushing complete. {} measurements".format(len(self.metrics.items())))

def main(metrics, *argv):
    # Initialize the logger
    logging.basicConfig(filename='/tmp/lineformat.log', format='%(asctime)s %(levelname)s %(message)s', filemode='a')
    logging.info("Starting up")

    # Intialize from our arguments
    try:
        lineformatsink = Lineformat(*argv[0:])
        lineformatsink.readmetrics(metrics.splitlines())
        lineformatsink.flush()
    except:
        logging.error("Caught exception", exc_info=True)


if __name__ == "__main__":
    # Get all the inputs
    main(sys.stdin.read(), *sys.argv[1:])

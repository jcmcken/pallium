import socket

# Gmetad settings
DEFAULT_GMETAD_PORT = 8651
DEFAULT_GMETAD_INT_PORT = 8652

class GangliaMetaDaemon(object):
    def __init__(self, host='localhost', port=DEFAULT_GMETAD_PORT, interactive_port=DEFAULT_GMETAD_INT_PORT,
                       connect=True):
        self.host = host
        self.port = port
        self.interactive_port = interactive_port
        self._sock = None
        self._int_sock = None

        if connect:
            self.connect()

    def __del__(self):
        self._int_sock.shutdown(socket.SHUT_RDWR)
        self._int_sock.close()
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()

    def connect(self):
        self._sock = self._connect(self.port)
        self._int_sock = self._connect(self.interactive_port)

    def _connect(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, port))
        return s

    def _stream_data(self, sock, bufsize=512):
        while True:
            recv = sock.recv(bufsize)
            if recv:
                yield recv
            else:
                break

    def _query(self, path):
        self._int_sock.send(path)
        return self._stream_data(self._int_sock)

    def query_cluster(self, cluster):
        return self._query("/" + cluster)

    def query_host(self, cluster, host):
        return self._query("/%s/%s" % (cluster, host))
        
    def query_cluster_summary(self, cluster):
        return self._query("/%s?filter=summary" % cluster)

    def query(self):
        return self._stream_data(self._sock)

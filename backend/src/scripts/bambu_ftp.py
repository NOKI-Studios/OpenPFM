"""
bambu_ftp.py – gemeinsame FTPS-Basisklasse für alle Bambu-Scripts.

Bambu-Drucker nutzen Implicit FTPS auf Port 990.
Die TLS-Session wird serverseitig nicht sauber geschlossen → quit() hängt.
Lösung: socket-Timeout + SIGALRM als harter Backstop.
"""

import ssl
import socket
import ftplib
import signal
import sys
import os

CONNECT_TIMEOUT = 8   # Sekunden für TCP + TLS Handshake
OP_TIMEOUT      = 120  # Sekunden für die eigentliche Operation (Upload)
TOTAL_TIMEOUT   = 150  # Harter Gesamttimeout


def _hard_timeout(signum, frame):
    sys.stderr.write("FTP TIMEOUT: Script wurde hart beendet\n")
    os._exit(1)


class ImplicitFTP_TLS(ftplib.FTP_TLS):
    """Implicit FTPS (Port 990) mit sofort aktiver TLS-Session."""

    def connect(self, host, port=990, timeout=CONNECT_TIMEOUT, **kwargs):
        self.host    = host
        self.port    = port
        self.timeout = timeout
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.settimeout(timeout)
        self.sock = ctx.wrap_socket(sock, server_hostname=host)
        self.af   = self.sock.family
        self.file = self.sock.makefile('r', encoding='utf-8', errors='replace')
        self.welcome = self.getresp()
        return self.welcome

    def quit_safe(self):
        """quit() hängt auf Bambu → socket hart schließen."""
        try:
            self.voidcmd("QUIT")
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass


def make_ftp(ip, access_code, op_timeout=OP_TIMEOUT):
    """Verbindet, authentifiziert und gibt ein fertiges FTP-Objekt zurück."""
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, _hard_timeout)
        signal.alarm(TOTAL_TIMEOUT)

    ftp = ImplicitFTP_TLS()
    ftp.connect(ip, 990, timeout=CONNECT_TIMEOUT)
    ftp.login("bblp", access_code)
    ftp.prot_p()
    ftp.set_pasv(True)
    # Socket-Timeout für alle nachfolgenden Operationen
    ftp.sock.settimeout(op_timeout)
    return ftp


def done():
    """Alarm deaktivieren nach erfolgreicher Operation."""
    if hasattr(signal, 'SIGALRM'):
        signal.alarm(0)
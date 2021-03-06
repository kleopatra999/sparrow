import functools
import os
import socket
import tempfile
import time
from six import BytesIO

import paramiko

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
__all__ = ['SSHConnection']

SSHException = paramiko.SSHException


def connection_required(f):
    """
    Connect to remote host if not yet connected
    """

    @functools.wraps(f)
    def wrapper(self, *args, **kw):
        """
        wrapper, connect to remote host if not yet connected
        """
        self.connect()
        return f(self, *args, **kw)

    return wrapper


class SSHConnection(object):
    """
    SSHConnection class, helper for using SSH client connections
    """

    def __init__(self, hostname, username=None, password=None,
                 port=22, debug=False, debug_file='/tmp/paramiko.log',
                 timeout=18000):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

        self.debug = debug
        self.debug_file = debug_file
        self.timeout = timeout

        self.connection = None

    def log(self, message):
        """
        Simple logger
        """
        if self.debug:
            print(message)

    def connect(self):
        """
        Connect to remote host
        """
        if self.connection:
            return

        hostname = self.hostname
        if self.debug:
            paramiko.util.log_to_file(self.debug_file)

        connection = paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connection.load_system_host_keys()
        connection.connect(hostname, username=self.username, password=self.password)
        self.connection = connection

    def close(self):
        """
        Close connection
        """
        if self.connection is not None:
            self.connection.close()

    @connection_required
    def read_file(self, name):
        """
        Get remote file using sftp protocol
        """
        ftp = self.connection.open_sftp()
        fh = ftp.open(name)
        s = fh.read()
        fh.close()
        ftp.close()
        return s

    @connection_required
    def upload_file(self, destination_name, source_file):
        """
        Uploads file to the server
        """
        transport = self.connection.get_transport()
        sftp = paramiko.SFTPClient.from_transport(transport)

        self.log("Copying %s as %s" % (source_file, destination_name))
        try:
            sftp.remove(destination_name)
        except IOError:
            pass # ignore
        sftp.put(source_file, destination_name)
        sftp.close()
        transport.close()

    @connection_required
    def write_file(self, destination_file, content):
        """
        Write content to the file on remote side
        """
        temp_file_name = None
        try:
            [fd, temp_file_name] = tempfile.mkstemp()
            temp_file = os.fdopen(fd, "w")
            temp_file.write(content)
            temp_file.close()

            self.upload_file(destination_file, temp_file_name)
        finally:
            if temp_file_name is not None:
                os.remove(temp_file_name)

    @connection_required
    def execute(self, cmd):
        """
        Execute a commend on remote host
        """
        try:
            logger.info('Running remote command: {} ...'.format(cmd))
            self.log(cmd)
            in_file, out_file, err_file = self.connection.exec_command(cmd, timeout=self.timeout, get_pty=True)
            channel = in_file.channel
            channel.shutdown_write()
            status = channel.recv_exit_status()

            stdout = out_file.read()
            stderr = err_file.read()

        except socket.timeout:
            raise SSHException("Socket timeout")


        logger.info('Exit code = {}'.format(status))
        logger.debug('Stdout:\n{}'.format(stdout))
        logger.debug('Stderr:\n{}'.format(stderr))
        return status, stdout, stderr

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import io
import os
import sys
import time
try:import httplib
except:import http.client as httplib
import ssl
import json
import websocket
try:import urllib2
except:import urllib.request as urllib2

try:unicode = unicode
except NameError:unicode = str


class IxNetError(Exception):
    '''Default IxNet error'''


class IxNet(object):
    """
    Set the IxNet object up
    """

    def __init__(self):
        self._websocket = None
        self._headers = None
        self._evalError = '1'
        self._evalSuccess = '0'
        self._evalResult = '0'
        self._addContentSeparator = 0
        self._firstItem = True
        self._sendContent = list()
        self._buffer = False
        self._sendBuffer = list()
        self._decoratedResult = list()
        self._debug = False
        self._async = False
        self._timeout = None
        self.OK = '::ixNet::OK'
        self.VERSION = '8.30.1077.21'

    def setDebug(self, debug):
        self._debug = debug
        return self

    def getRoot(self):
        return str('::ixNet::OBJ-/')

    def getNull(self):
        return str('::ixNet::OBJ-null')

    def setAsync(self):
        self._async = True
        return self

    def setTimeout(self, timeout):
        self._timeout = timeout
        return self

    def getApiKey(self, hostname, username, password, apiKeyFile='api.key'):
        self._setup_connection(hostname)
        auth = self._rest_send('POST', '/api/v1/auth/session',
            payload={'username': username, 'password': password})
        self._headers = {
            'X-Api-Key': auth.apiKey
        }
        with open(apiKeyFile, 'w') as api_key_file:
            api_key_file.write(auth.apiKey)
        return auth.apiKey

    def _create_headers(self, default_args):
        apiKeyValue = ''
        if len(str(default_args['-apiKey'])) > 0:
            apiKeyValue = default_args['-apiKey']
        elif len(str(default_args['-apiKeyFile'])) > 0:
            with open(str(default_args['-apiKeyFile']), 'r') as api_key_file:
                apiKeyValue = api_key_file.read()
        self._headers = {
            'X-Api-Key': apiKeyValue
        }

    def getSessions(self, hostname, *args):
        if self._is_connected(raiseError=False) is False:
            default_args = {
                '-apiKey': '',
                '-apiKeyFile': 'api.key'
            }
            session_args = self._get_arg_map(default_args, *args)
            self._setup_connection(hostname)
            self._create_headers(session_args)
        sessionsUrl = '/api/v1/sessions'
        response = self._rest_send('GET', sessionsUrl)
        sessions = dict()
        if isinstance(response, list) is False:
            response = [response]
        for session in response:
            if str(session.state).lower() == 'active':
                sessionUrl = '{0}/{1}'.format(sessionsUrl, session.id)
                ixnetworkUrl = '{0}/ixnetwork'.format(sessionUrl)
                ixnet = self._rest_send('GET', '{0}/globals/ixnet'.format(ixnetworkUrl))
                if ixnet is not None:
                    data = {
                            'id': session.id,
                            'url': 'https://{0}{1}'.format(self._base_url, ixnetworkUrl),
                            'state': session.state,
                            'inUse': ixnet.isActive,
                            'connectedClients': ixnet.connectedClients,
                            'sessionUrl': 'https://{0}{1}'.format(self._base_url, sessionUrl)
                        }
                    sessions[session.id] = data
        return sessions
    
    def clearSessions(self, hostname, *args):
        deleted_sessions = []
        sessions = self.getSessions(hostname, *args)
        for sessionId in sessions:
            session = sessions[sessionId]
            ixnet = self._rest_send('GET', '{0}/globals/ixnet'.format(session['url']))
            if ixnet.isActive is False:
                operation = self._rest_send('POST', '{0}/operations/stop'.format(session['sessionUrl']))
                while operation.progress != 100:
                    time.sleep(2)
                    operation = self._rest_send('GET', operation.url)
                self._rest_send('DELETE', session['sessionUrl'])
                deleted_sessions.append(session['sessionUrl'])
        return deleted_sessions

    def getSessionInfo(self):
        self._is_connected(raiseError=True)
        session_info = {
            'url': 'https://{0}{1}'.format(self._base_url, self._rest_url)
        }
        session = self._rest_send('GET', '{0}/globals/ixnet'.format(self._rest_url))
        session_info['inUse'] = session.isActive
        session_info['connectedClients'] = session.connectedClients
        return session_info

    def _setup_connection(self, hostname):
        self._headers = {}
        self._base_url = hostname
        self._ssl_context = ssl.SSLContext(2)
        self._ssl_context.check_hostname = False
        self._connection = httplib.HTTPSConnection(self._base_url, context=self._ssl_context)

    def _rest_send(self, method, url, payload=None, fid=None, file_content=None):
        headers = self._headers
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            self._connection.request(method, url, body=json.dumps(payload), headers=headers)
        elif fid is not None:
            headers['Content-Type'] = 'application/octet-stream'
            self._connection.request(method, url, body=fid, headers=headers)
        elif file_content is not None:
            headers['Content-Type'] = 'application/octet-stream'
            self._connection.request(method, url, body=json.dumps(file_content), headers=headers)
        else:
            self._connection.request(method, url, headers=headers)
        response = self._connection.getresponse()
        content = response.read()
        if str(response.status).startswith('2') is False:
            raise IxNetError(content)
        if len(content):
            contentObject = json.loads(content)
            if isinstance(contentObject, list):
                data_list = []
                for contentItem in contentObject:
                    data = lambda: None
                    data.__dict__ = contentItem
                    data_list.append(data)
                return data_list
            else:
                data = lambda: None
                data.__dict__ = contentObject
                return data
        else:
            return None

    def _get_arg_map(self, default_args, *args):
        name = None
        for arg in args:
            if str(arg).startswith('-'):
                name = str(arg)
            elif name is not None:
                default_args[name] = str(arg)
                name = None
        return default_args

    def connect(self, hostname, *args):
        if self._is_connected(raiseError=False):
            print("A connection already exists to session {0}".format(self._session_url))
            return self.OK
        try:
            default_args = {
                '-sessionId': 0,
                '-version': '5.30',
                '-connectTimeout': 120,
                '-apiKey': '',
                '-apiKeyFile': 'api.key',
                '-product': 'ixnrest'
            }
            connect_args = self._get_arg_map(default_args, *args)

            # create a session if a valid sessionId has not been specified
            url = '/api/v1/sessions'
            if connect_args['-sessionId'] < 1:
                self._setup_connection(hostname)
                self._create_headers(connect_args)
                session = self._rest_send('POST', url, {"applicationType": connect_args['-product']})
            else:
                sessions = self.getSessions(hostname, args)
                session = lambda: None
                session.__dict__ = sessions[int(connect_args['-sessionId'])]

            # start the session
            sessionId = session.id
            url = '{0}/{1}'.format(url, sessionId)
            self._session_url = url
            if str(session.state).lower() == "initial":
                async_operation_result = self._rest_send('POST', 
                    '{0}{1}'.format(self._session_url, '/operations/start'), 
                    payload={'applicationType': 'ixnetwork'})
            
            # wait for session to go active in connectTimeout seconds
            start_time = int(time.time())
            while int(time.time()) - start_time < int(connect_args['-connectTimeout']):
                session = self._rest_send('GET', self._session_url)
                if str(session.state).lower() == 'active':
                    self._rest_url = '{0}/ixnetwork'.format(url)
                    self._ws_url = 'wss://{0}/ixnrest/ws/api/v1/sessions/{1}/ixnetwork/globals/ixnet'.format(self._base_url, sessionId)
                    options = dict({
                        'sslopt': {
                            'cert_reqs': ssl.CERT_NONE,
                            'check_hostname': False
                        }
                    })
                    self._websocket = websocket.create_connection(self._ws_url, timeout=10, **options)
                    self._websocket.settimeout(300)
                    result = self._send_recv('ixNet', 'connect', 
                        '-version', connect_args['-version'], 
                        '-clientType', 'python',
                        '-closeServerOnDisconnect', 'true',
                        '-apiKey', self._headers['X-Api-Key'])
                    self._check_client_version()
                    return result
                time.sleep(2)
            raise Exception('IxNetwork instance {0} did not start within {1} seconds.'.format(sessionId, connect_args['-connectTimeout']))

        except:
            e = sys.exc_info()[1]
            self._close()
            raise IxNetError('Unable to connect to {0}. Error:{1}'.format(hostname, str(e)))
    
    def disconnect(self):
        if self._is_connected(raiseError=True):
            self.setSessionParameter("closeServerOnDisconnect", "true")
            self._close()
            time.sleep(5)
        return self.OK

    def help(self, *args):
        return self._send_recv('ixNet', 'help', *args)

    def setSessionParameter(self, *args):
        if len(args) % 2 == 0:
            return self._send_recv('ixNet', 'setSessionParameter', *args)
        else:
            raise IxNetError(
                'setSessionParameter requires an even number of name/value pairs')

    def getVersion(self):
        if self._is_connected():
            return self._send_recv('ixNet', 'getVersion')
        else:
            return self.VERSION

    def getParent(self, objRef):
        return self._send_recv('ixNet', 'getParent', objRef)

    def exists(self, objRef):
        return self._send_recv('ixNet', 'exists', self._check_obj_ref(objRef))

    def commit(self):
        return self._send_recv('ixNet', 'commit')

    def rollback(self):
        return self._send_recv('ixNet', 'rollback')

    def execute(self, *args):
        return self._send_recv('ixNet', 'exec', *args)

    def add(self, objRef, child, *args):
        return self._send_recv('ixNet', 'add', self._check_obj_ref(objRef), child, *args)

    def remove(self, objRef):
        return self._send_recv('ixNet', 'remove', objRef)

    def setAttribute(self, objRef, name, value):
        self._buffer = True
        return self._send_recv('ixNet', 'setAttribute', self._check_obj_ref(objRef), name, value)

    def setMultiAttribute(self, objRef, *args):
        self._buffer = True
        return self._send_recv('ixNet', 'setMultiAttribute', self._check_obj_ref(objRef), *args)

    def getAttribute(self, objRef, name):
        return self._send_recv('ixNet', 'getAttribute', self._check_obj_ref(objRef), name)

    def getList(self, objRef, child):
        return self._send_recv('ixNet', 'getList', self._check_obj_ref(objRef), child)

    def getFilteredList(self, objRef, child, name, value):
        return self._send_recv('ixNet', 'getFilteredList', self._check_obj_ref(objRef), child, name, value)

    def adjustIndexes(self, objRef, object):
        return self._send_recv('ixNet', 'adjustIndexes', self._check_obj_ref(objRef), object)

    def remapIds(self, localIdList):
        if type(localIdList) is tuple:
            localIdList = list(localIdList)
        return self._send_recv('ixNet', 'remapIds', localIdList)

    def getResult(self, resultId):
        return self._send_recv('ixNet', 'getResult', resultId)

    def wait(self, resultId):
        return self._send_recv('ixNet', 'wait', resultId)

    def isDone(self, resultId):
        return self._send_recv('ixNet', 'isDone', resultId)

    def isSuccess(self, resultId):
        return self._send_recv('ixNet', 'isSuccess', resultId)

    def writeTo(self, filename, *args):
        if any(arg == '-ixNetRelative' for arg in args):
            return self._send_recv('ixNet', 'writeTo', filename, '\02'.join(args))
        else:
            return self._create_file_on_server(filename)

    def readFrom(self, filename, *args):
        if any(arg == '-ixNetRelative' for arg in args):
            return self._send_recv('ixNet', 'readFrom', filename, '\02'.join(args))
        else:
            return self._put_file_on_server(filename)

    def _check_obj_ref(self, objRef):
        if (type(objRef) in (str, unicode)) is False:
            raise IxNetError('The objRef parameter must be ' +
                             str(str) + ' instead of ' + str(type(objRef)))
        else:
            return objRef

    def _put_file_on_server(self, filename):
        filename = os.path.basename(filename)
        files = self._rest_send('GET', '{0}/files'.format(self._rest_url))
        remote_filename = '{0}/{1}'.format(files.absolute, filename)
        with io.open(filename, 'rb') as fid:
            self._rest_send('POST', '{0}/files?filename={1}'.format(self._rest_url, filename), fid=fid)
        return self._send_recv('ixNet', 'readFrom', remote_filename, '-ixNetRelative')

    def _create_file_on_server(self, filename):
        local_filename = filename
        filename = os.path.basename(filename)
        files = self._rest_send('GET', '{0}/files'.format(self._rest_url))
        remote_filename = '{0}/{1}'.format(files.absolute, filename)
        self._rest_send('POST', '{0}/files?filename={1}'.format(self._rest_url, filename), file_content={})
        return self._send_recv('ixNet', 'writeTo', remote_filename, '-ixNetRelative', '-overwrite', '-remote', local_filename)

    def _close(self):
        try:
            if self._websocket is not None:
                self._websocket.close()
        except:
            sys.exc_clear()
        self._websocket = None

    def _join(self, *args):
        for arg in args:
            if type(arg) is list or type(arg) is tuple:
                if self._addContentSeparator == 0:
                    self._sendContent.append('\02')
                if self._addContentSeparator > 0:
                    self._sendContent.append('{')
                self._addContentSeparator += 1
                self._firstItem = True
                if len(arg) == 0:
                    self._sendContent.append('{}')
                else:
                    for item in arg:
                        self._join(item)
                if self._addContentSeparator > 1:
                    self._sendContent.append('}')
                self._addContentSeparator -= 1
            else:
                if self._addContentSeparator == 0 and len(self._sendContent) > 0:
                    self._sendContent.append('\02')
                elif self._addContentSeparator > 0:
                    if self._firstItem is False:
                        self._sendContent.append(' ')
                    else:
                        self._firstItem = False
                if arg is None:
                    arg = ''
                elif type(arg) != str:
                    arg = str(arg)
                if len(arg) == 0 and len(self._sendContent) > 0:
                    self._sendContent.append('{}')
                elif arg.find(' ') != -1 and self._addContentSeparator > 0:
                    self._sendContent.append('{' + arg + '}')
                else:
                    self._sendContent.append(arg)

        return

    def _send_recv(self, *args):
        self._is_connected(raiseError=True)
        self._addContentSeparator = 0
        self._firstItem = True

        argList = list(args)

        if self._async:
            argList.insert(1, '-async')

        if self._timeout is not None:
            argList.insert(1, '-timeout')
            argList.insert(2, self._timeout)

        for item in argList:
            self._join(item)

        self._sendContent.append('\03')
        self._sendBuffer.append(''.join(self._sendContent))
        if self._buffer is False:
            buffer = ''.join(self._sendBuffer)
            if self._debug:
                print('Sending: ', buffer)
            self._send('<001><002><009{0}>{1}'.format(len(buffer), buffer))
            self._sendBuffer = list()

        self._async = False
        self._timeout = None
        self._buffer = False
        self._sendContent = list()

        if len(self._sendBuffer) > 0:
            return self.OK
        else:
            return self._recv()

    def _send(self, content):
        try:
            if type(content) is str:
                content = content.encode('ascii')
            self._websocket.send(content)
        except (socket.error,):
            e = sys.exc_info()[1]
            self._close()
            raise IxNetError('Error:' + str(e))

    def _recv(self):
        self._decoratedResult = list()
        responseBuffer = str()
        try:
            responseBuffer = self._websocket.recv().decode('ascii')
            commandId = None
            contentLength = int(0)
            while len(responseBuffer) > 0:
                startIndex = int(responseBuffer.find('<'))
                stopIndex = int(responseBuffer.find('>'))
                if startIndex != -1 and stopIndex != -1:
                    commandId = int(
                        responseBuffer[startIndex + 1 : startIndex + 4])
                    if startIndex + 4 < stopIndex:
                        contentLength = int(
                            responseBuffer[startIndex + 4 : stopIndex])
                stopIndex += 1
                if commandId == 1:
                    self._evalResult = self._evalError
                elif commandId == 4:
                    self._evalResult = responseBuffer[stopIndex : stopIndex + contentLength]
                elif commandId == 7:
                    filename = responseBuffer[stopIndex : stopIndex + contentLength]
                    remoteFilename = os.path.basename(filename)
                    file_url = 'https://{0}{1}/files?filename={2}'.format(self._base_url, self._rest_url, remoteFilename)
                    request = urllib2.Request(file_url, headers=self._headers)
                    response = urllib2.urlopen(request, context=self._ssl_context)
                    with open(filename, "wb") as fid:
                        fid.write(response.read())
                elif commandId == 9:
                    self._decoratedResult = responseBuffer[stopIndex : stopIndex + contentLength]
                responseBuffer = responseBuffer[stopIndex + contentLength :]
        except:
            e = sys.exc_info()[1]
            self._close()
            raise IxNetError('Recv failed. Error:' + str(e))

        if self._debug:
            print('Received: ', ''.join(self._decoratedResult))

        if self._evalResult == self._evalError:
            raise IxNetError(''.join(self._decoratedResult))

        if len(self._decoratedResult) > 0 and self._decoratedResult[0].startswith('\01'):
            return eval(''.join(self._decoratedResult[1:]))
        else:
            return ''.join(self._decoratedResult)

    def _check_client_version(self):
        version = self.getVersion()
        if self.VERSION != version:
            print('WARNING: IxNetwork Python library version {0} does not match the IxNetwork client version {1}'.format(self.VERSION, version))

    def _is_connected(self, raiseError=False):
        if self._websocket is None:
            if raiseError is True:
                raise IxNetError('not connected')
            else:
                return False
        else:
            return True

# Dreampylib - version 1.0
# (c) 2009 by Laurens Simonis
# See dreampylib_license.txt for licencing info

# UUID is needed to generate a nice random uuid for dreamhost
import uuid
from urllib.request import urlopen
from urllib.parse import urlencode


defaultReturnType = 'dict'


class _RemoteCommand(object):
    # some magic to catch arbitrary maybe non-existent func. calls
    # supports "nested" methods (e.g. examples.getStateName)
    def __init__(self, name, parent, url, debug=False):

        # Store the name of the
        self._name = name
        self._cmd = name.replace('.', '-')
        self._parent = parent
        self._url = url
        self._child = None
        self._debug = debug

        self._resultKeys = []
        self._status = ""
        self._resultDict = []
        self._resultList = []

    def Status(self):
        if self._child:
            return self._child.Status()
        else:
            return self._status

    def ResultKeys(self):
        if self._child:
            return self._child.ResultKeys()
        else:
            return self._resultKeys

    def ResultList(self):
        if self._child:
            return self._child.ResultList()
        else:
            return self._resultList

    def ResultDict(self):
        if self._child:
            return self._child.ResultDict()
        else:
            return self._resultDict

    def __getattr__(self, name):
        self._child = _RemoteCommand(
            "%s.%s" % (self._name, name), self._parent, self._url
        )
        return self._child

    def __call__(self, returnType=None, *args, **kwargs):
        if self._debug:
            print("Called %s(%s)" % (self._name, str(kwargs)))

        if self._parent.IsConnected():

            request = {}
            request.update(kwargs)
            request.update(self._parent._GetUserData())

            request['cmd'] = self._cmd
            request['unique_id'] = str(uuid.uuid4())

            if self._debug:
                print(request)

            self._connection = urlopen(
                self._url,
                urlencode(request).encode('utf-8')
            )
            return self._ParseResult(returnType or defaultReturnType)
        else:
            return []

    def _ParseResult(self, returnType):
        '''Parse the result of the request'''
        lines = [l.decode('utf-8').strip() for l in self._connection.readlines()]

        if self._debug:
            print("response", lines)

        self._status = lines[0]

        if self._status == 'success':
            self._resultKeys = keys = lines[1].split('\t')

            table = []
            for resultLine in lines[2:]:
                    values = resultLine.split('\t')
                    self._resultDict.append(dict(zip(keys, values)))
                    if len(values) == 1:
                        self._resultList.append(values[0])
                    else:
                        self._resultList.append(values)

            if returnType == 'list':
                table = self._resultList
            else:
                table = self._resultDict

            if self._debug:
                for t in table:
                    print(t)

            return table

        else:
            if self._debug:
                print('ERROR with %s: %s - %s' % (
                    self._name, lines[0], lines[1]
                ))
            self._status = '%s: %s - %s' % (self._name, lines[0], lines[1])
            return False, lines[0], lines[1]


class DreampyLib(object):
    def __init__(self, key=None, url='https://api.dreamhost.com', debug=False):
        '''Initialises the connection to the dreamhost API.'''

        self._key = key
        self._url = url
        self._lastCommand = None
        self._connected = False
        self._availableCommands = []
        self._debug = debug

        if key:
            self.Connect()

    def Connect(self, key=None, url=None):
        if key:
            self._key = key

        if url:
            self._url = url

        if self._debug:
            print("connecting to url", self._url, "with key", self._key)

        self._connected = True
        self._availableCommands = \
            self.api.list_accessible_cmds(returnType='list')
        self._connected = self._availableCommands[0] is not False
        if not self._connected:
            self._availableCommands = []
            return False
        return True

    def AvailableCommands(self):
        return self._availableCommands

    def IsConnected(self):
        return self._connected

    def ResultKeys(self):
        if not self._lastCommand:
            return []
        else:
            return self._lastCommand.ResultKeys()

    def ResultList(self):
        if not self._lastCommand:
            return []
        else:
            return self._lastCommand.ResultList()

    def ResultDict(self):
        if not self._lastCommand:
            return []
        else:
            return self._lastCommand.ResultDict()

    def Status(self):
        if not self._lastCommand:
            return None
        else:
            return self._lastCommand.Status()

    def _GetUserData(self):
        return {
            'key':       self._key,
        }

    def __getattr__(self, name):
        self._lastCommand = _RemoteCommand(name, self, self._url, self._debug)
        return self._lastCommand

    def dir(self):
        self.api.list_accessible_cmds()

if __name__ == '__main__':
    import pprint

    # Dreamhost test API account:
    key = '6SHU5P2HLDAYECUM'

    # Set this to true to enable debugging
    DEBUG = False

    # Specify the default returntype.
    # Can be either 'dict' or 'list'
    defaultReturnType = 'dict'

    # Initialize the library and open a connection
    connection = DreampyLib(key, debug=DEBUG)

    # If the connection is up, do some tests.
    if connection.IsConnected():
        # For instance, list the available commands:
        print('Available commands:\n ',)
        listOfCommands = connection.AvailableCommands()
        pprint.pprint(listOfCommands)
        # print('\n  '.join(listOfCommands))

        # Even if defaultReturnType is 'dict',
        # you can get the last result as a list, too.

        print(type(connection.dreamhost_ps.list_size_history(ps='ps7093')))
        print(type(connection.ResultList()))
    else:
        print("Error connecting!")
        print(connection.Status())

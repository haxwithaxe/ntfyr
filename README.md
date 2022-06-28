# Description
A simple tool to make sending notifications to ntfy.sh or your self-hosted instance easy and clean.


# Usage
Example: `echo test failure | ntfyr -t test -s http://ntfy.sh -G skull,failure -T 'Bad thing happened!'`

```sh
ntfyr [-h] [-A ACTIONS] [-X ATTACH] [-C CLICK] [-D DELAY] [-E EMAIL]
             [-P {max,urgent,high,default,low,min,1,2,3,4,5}]
             [-G TAGS [TAGS ...]] [-T TITLE] [-m MESSAGE] -t TOPIC [-s SERVER]
             [-u USER] [-p PASSWORD] [-c CONFIG] [--debug]
```

## Arguments
```sh
  -t TOPIC, --topic TOPIC              The topic to send the notification to. Required.
  -s SERVER, --server SERVER           The server to send the notification to. Defaults to https://ntfy.sh.
  -u USER, --user USER                 The user to authenticate to the server with.
  -p PASSWORD, --password PASSWORD     The password to authenticate to the server with.
  -c CONFIG, --config CONFIG           The configuration file with default values. The values specified as arguments override the values in this file.
  -m MESSAGE, --message MESSAGE        The body of the message to send. The default (or if "-"is given) is to read from stdin.
  -h, --help                           Show this help message and exit
  --debug                              Show extra information in the error messages.
```

The following specify metadata (headers). See https://ntfy.sh/docs/publish/ for more information.
```sh
  -A ACTIONS, --actions ACTIONS
  -X ATTACH, --attach ATTACH
  -C CLICK, --click CLICK
  -D DELAY, --delay DELAY
  -E EMAIL, --email EMAIL
  -P {max,urgent,high,default,low,min,1,2,3,4,5}, --priority {max,urgent,high,default,low,min,1,2,3,4,5}
  -G TAGS [TAGS ...], --tags TAGS [TAGS ...]
  -T TITLE, --title TITLE
```

# Install
* Install via pip: ```pip install ntfyr```
* Install manually: 
```sh
git clone https://github.com/haxwithaxe/ntfyr.git
cd ntfyr
python3 setup.py install
```

# Configuration
No configuration is reqired. However a config file with default values can be given via `-c path/to/config.ini`, `--config path/to/config.ini`, or in the default location at `/etc/ntfyr/config.ini`.
Any of the long options (options beginning with `--`) without the leading dashes can be used to specify a default value for that option. For example the following sets a default server and credentials:
```
[ntfyr]
server = http://ntfy.example.com
user = alice
password = supersecret
```

Commandline arguments override config values. Passing an option with an empty string will disable the default value in the config file. For example the following will disable the authentication that the above config enables:
```ntfyr --user '' --password '' -t mytopic -m 'Hello world!'```


# Dependencies
This module depends on `requests`.

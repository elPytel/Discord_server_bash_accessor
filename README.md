# Discord server bash accessor
This is a discord bot that allows you to run bash commands on the host machine and send files from it.

## Instalation 
### Automatic
Run `install.sh` script and grant it root axcess to install service and all dependencies.

### Manual
#### pip dependencies
``` bash
pip install -r requirements.txt
```

#### Configuration
Run apllication with option `python3 main.py --config` to create a config file. You nead to do it set the API key and server ID.

#### Demonization
Change path your scipt
Copy `discordBashAccessor.service` to `/etc/systemd/system/`.

Now we need to reload the daemon.
``` bash
sudo systemctl daemon-reload
```

Let’s enable our service so that it doesn’t get disabled if the server restarts.
``` bash
sudo systemctl enable discordBashAccessor.service
```

And now let’ start our service.
``` bash
sudo systemctl start discordBashAccessor.service
```

Now our service is up and running.

#### Other commands for service
There are several commands you can do to start, stop, restart, and check status.

To stop the service.
``` bash
sudo systemctl stop discordBashAccessor.service
```

To restart.
``` bash
sudo systemctl restart discordBashAccessor.service
```

To check status.
``` bash
sudo systemctl status discordBashAccessor.service
```

## Usage
Bot will be online when you start service. 
### Commands

#### Run
Will run bash command o host machine and return output.
```
$run "bash command"
```

#### File
Will send file from host machine.
```
$file "path to file"
```
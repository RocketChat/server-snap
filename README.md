![Rocket.Chat logo](https://rocket.chat/images/logo/logo-dark.svg?v3)

# rocketchat-server snap for Ubuntu Core  (all arch)

Features:
* bundles ubuntu distribution specific and RC compatible mongodb version
* oplog tailing for mongo by default
* mongodb backup command  
* mongodb restore command
* caddy reverse proxy built-in - capable of handling free lestencrypt ssl

Note:

Currently, this repository is mirrored on launchpad, and used to build latest ARMHF and i386 snaps.   

You can download recent builds here:
https://code.launchpad.net/~sing-li/+snap/rocketchat-server

Due an issue with the existing installed base of amd64 users (existing snap always installed mongodb 3.2  [#issue](https://github.com/RocketChat/rocketchat-server-snap/issues/3)), this snap is not currently used for amd64 builds.

### Test installation 

Download the latest snap file of the corresponding architecture to your Ubuntu Core 16 or 16.04LTS server.

`sudo snap install ./rocketchat-server-xxxxxxxx.snap  --dangerous`


### Development or compile your own snap

Make sure you have `snapcraft` installed.

```
git clone https://github.com/RocketChat/rocketchat-server-snap
cd rocketchat-server-snap
snapcraft snap
```



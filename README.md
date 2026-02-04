# Philips TV Remote

Web frontend to control old Philips TVs.

This replaces the physical remote and the discontinued "My Remote" app.
Host this on a small computer (eg. a Raspberry Pi or NAS) in the same network as the TV.
Before running it, change the path in `tv_remote.service` and the TV IP in `proxy.py`.
For convenience, visit the webpage on a smartphone and add a shortcut to the homescreen.

To change the available channels, use
```
wget http://<TV_IP>:1925/1/channels
```
and update `channels.json`.

Disclaimer: the frontend and `proxy.py` are vibecoded and there are some obvious security flaws. Only deploy this in a safe environment and do not expose it to the internet.

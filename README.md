# flightrecorder

This script was inspired by the amazing work of [AirtagAlex](https://github.com/icepick3000/AirtagAlex), as well as a bit of[clara-j's](https://github.com/clara-j/AirTagRecorder) adaptation.

I wrote it because I had occasion to need to troubleshoot some shipment problems. There was a particular shipping scenario I was experiencing problems with, so inspired by Alex's AirTag "tourism" project, I stuck an AirTag inside an old wallet, boxed it up, and mailed it to the problemtatic destination.

I further followed Alex's tutorial on how to remove the speaker from the AirTag before shipping, so that it didn't start making a bunch of noise while in the mailroom and totally freak some poor admin staff person out.

The script is quite simple to use. It doesn't require anything other than Python modules that come with the base distribution. My Mac was using Python 3.10.6, from macOS Homebrew, currently running on macOS 12.5. Temp files and CSV output will be in your current directory. You can just invoke it as simply as ./flightrecorder.py.

By default, the script will record data on all AirTags associated with your iCloud account. Optionslly, you can specify the -s / --serial option, along with a serial number, and the script will only record data for that one AirTag.

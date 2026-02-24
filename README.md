# bussinFR

Realtime GTFS bus information on a web page, currently hosted at
[https//bussinfr.net](https://bussinfr.net)


If you're interested in the FastAPI interface, then have a look at :
```
webservices/bussinAPIs.py
```

The gist is as follows :

The vehicle position and trip update data arrive 
in General Transit Feed Specification (GTFS)
format (a format based on Protocol Buffers). As I understand it,
in order to achieve the rapid-fire nature of the data, the data must
be obtained in an all-or-nothing manner (so you can't ask for a limited
subset of the data). 

The bus stop data arrive via a different (much slower)
mechanism, in that a comma separated variable list file
is downloaded, generally on a weekly basis.

All these data are then stored in simple sqlite databases,
which facilitates requests for a subset of the data through
a FastAPI interface.

This then feeds into the web page, which uses the Leaf javaScript mapping
library to display the data.

Several cron jobs are used to ensure that the required servers
keep running. Other methods of doing this (like systemd units) are
certainly possible, but in the interest of keeping the code accessible this simple
cron approach was taken.

The web page is served out using nginx, with a proxy to the internal
port that uvicorn serves the FastAPI out on (see the superUserStuff/
directory).

At the time of writing this runs on a Digital Ocean "droplet"
server in San Francisco running Ubuntu.


geolocate.py
============
This library lets you turn an IP address into a physical location.
The data that comes with it is extremely rough, and may not be accurate in any meaningful way.

The purpose of this library is to allow you to look up thousands and thousands and thousands of IPs without annoying an online provider of geolocation services, or giving them money, or waiting for the response time for each request.

It also lets you do this without defining a location for each of the 4294967295-ish available IPs in IPv4, because that's an awful lot of memory.

usage:

`import geolocate`
`geo = geolocate.geolocate()`
`location = geo.get(ip)`
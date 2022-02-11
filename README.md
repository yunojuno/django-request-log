# Django Request Log

Simple Django model for logging HttpRequest instances.

## Why?

We have a number of libraries that store elements of a request (path,
querystring, user, response code, remote_addr, and so on), and it seemed
like time to create a single model that we can use in all of them,
storing a common set of values.

## Why not?

This is not a replacement for web server logs - it's a utility for use
in specific situations where you want to accurately log that someone
requested something.

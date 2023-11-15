# Django Request Log

Simple Django model for logging HttpRequest instances.

## Why?

We have a number of libraries that store elements of a request (path,
querystring, user, response code, remote_addr, and so on), and it seemed
like time to create a single model that we can use in all of them,
storing a common set of values.

This is not a replacement for web server logs - it's a utility for use
in specific situations where you want to accurately log that someone
requested something.

## How it works

There is a single model, `RequestLog` and a model manager with a
`create` method that can take in a standard `HttpRequest` and / or
`HttpResponse` object and create a new `RequestLog` object. If you
are using this to record view functions, there is also a decorator,
`log_request` that will take care of all this for you:

```python
from request_logger.decorators import log_request

@log_request("downloads")
def download(request: HttpRequest) -> HttpReponse:
    return HttpResponse("OK")
    

@log_request(lambda r: r.user.get_full_name())
def download(request: HttpRequest) -> HttpReponse:
    return HttpResponse("OK")
```

The `log_request` argument is mandatory and is used as a "reference",
or category classifier. It can be a str, or a callable which takes
in the request as a single arg.

## Screenshots

**Admin list view**

<img src="screenshots/admin-list.png">

**Admin item view**

<img src="screenshots/admin-edit.png">

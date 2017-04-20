from collections import deque
from inspect import isawaitable
from traceback import format_exc

from sanic import Sanic
from sanic.exceptions import ServerError
from sanic.log import log
from sanic.response import HTTPResponse
from sanic.response import json

from base.exception import BaseExcep


class Application(Sanic):
    def __init__(self, route_dict, err_route, middlewmare, env):
        assert isinstance(route_dict, dict)
        assert isinstance(middlewmare, dict)
        assert isinstance(err_route, dict)

        super(Application, self).__init__()
        for k, v in route_dict.items():
            self._add_route(v, k)
        for k, v in err_route.items():
            self.error_handler.add(k, v)

        self.env = env
        self.request_middleware = deque(
            middlewmare['request']) if 'request' in middlewmare else deque()
        self.response_middleware = deque(
            middlewmare['response']) if 'response' in middlewmare else deque()

    def middleware(self, *args, **kwargs):
        raise NotImplementedError

    def route(self, uri, methods=frozenset({'GET'}), host=None,
              strict_slashes=False):
        raise NotImplementedError

    def _route(self, uri, methods=frozenset({'GET'}), host=None,
               strict_slashes=False):
        """Decorate a function to be registered as a route

        :param uri: path of the URL
        :param methods: list or tuple of methods allowed
        :param host:
        :return: decorated function
        """

        # Fix case where the user did not prefix the URL with a /
        # and will probably get confused as to why it's not working
        if not uri.startswith('/'):
            uri = '/' + uri

        def response(handler):
            self.router.add(uri=uri, methods=methods, handler=handler,
                            host=host, strict_slashes=strict_slashes)
            return handler

        return response

    def _add_route(self, handler, uri, methods=frozenset({'POST', 'GET'}), host=None,
                   strict_slashes=False):
        """A helper method to register class instance or
        functions as a handler to the application url
        routes.

        :param handler: function or class instance
        :param uri: path of the URL
        :param methods: list or tuple of methods allowed, these are overridden
                        if using a HTTPMethodView
        :param host:
        :return: function or class instance
        """
        # Handle HTTPMethodView differently
        # if hasattr(handler, 'view_class'):
        #     methods = set()
        #
        #     for method in HTTP_METHODS:
        #         if getattr(handler.view_class, method.lower(), None):
        #             methods.add(method)
        #
        # # handle composition view differently
        # if isinstance(handler, CompositionView):
        #     methods = handler.handlers.keys()

        self._route(uri=uri, methods=methods, host=host,
                    strict_slashes=strict_slashes)(handler)
        return handler

    def add_route(self, handler, uri, methods=frozenset({'GET'}), host=None,
                  strict_slashes=False):
        raise NotImplementedError

    async def handle_request(self, request, write_callback=None, stream_callback=None):
        """
        Takes a request from the HTTP Server and returns a response object to
        be sent back The HTTP Server only expects a response object, so
        exception handling must be done here
        :param request: HTTP Request object
        :param response_callback: Response function to be called with the
        response as the only argument
        :return: Nothing
        """
        try:
            # -------------------------------------------- #
            # Request Middleware
            # -------------------------------------------- #

            response = False
            # The if improves speed.  I don't know why
            if self.request_middleware:
                for middleware in self.request_middleware:
                    response = middleware(request, env=self.env)
                    if isawaitable(response):
                        response = await response
                    if response:
                        break

            # No middleware results
            if not response:
                # -------------------------------------------- #
                # Execute Handler
                # -------------------------------------------- #

                # Fetch handler from router
                handler, args, kwargs = self.router.get(request)
                if handler is None:
                    raise ServerError(
                        ("'None' was returned while requesting a "
                         "handler from the router"))

                # Run response handler
                response = handler(request, self.env, *args, **kwargs)()
                if isawaitable(response):
                    response = await response

                # -------------------------------------------- #
                # Response Middleware
                # -------------------------------------------- #

                if self.response_middleware:
                    for middleware in self.response_middleware:
                        _response = middleware(request, response, env=self.env)
                        if isawaitable(_response):
                            _response = await _response
                        if _response:
                            response = _response
                            break
        except BaseExcep as e:
            if e.log:
                log.exception(e.args)

            response = json({'code': e.code, 'data': e.data, 'id': None,
                             'msg': e.msg}, 200)
        except Exception as e:
            # -------------------------------------------- #
            # Response Generation Failed
            # -------------------------------------------- #
            try:
                log.exception(e.args)
                response = self.error_handler.response(request, e)
                if isawaitable(response):
                    response = await response

                if response.status == 500:
                    if self.debug:
                        response = json({'code': -1, 'data': format_exc(),
                                         'msg': e.__repr__(), 'id': None}, 200)
                    else:
                        response = json({'code': -1, 'data': e.__repr__(),
                                         'msg': '系统出错', 'id': None}, 200)
            except Exception as e:
                if self.debug:
                    response = HTTPResponse(
                        "Error while handling error: {}\nStack: {}".format(
                            e, format_exc()))
                else:
                    response = HTTPResponse(
                        "An error occured while handling an error")

        write_callback(response)

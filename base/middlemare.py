
from sanic.request import Request
from sanic import Blueprint, Sanic


class MjsonMiddlemare:

    @staticmethod
    @Sanic.middleware('request')
    def setup(request):
        assert isinstance(request, Request)
        MjsonMiddlemare.setup_identification(request)
        MjsonMiddlemare.setup_session(request)
        MjsonMiddlemare.fix_lang(request)

    @staticmethod
    def setup_identification(req):
        assert isinstance(req, Request)
        setattr(req, 'identification', req.json.get('identication'))
        setattr(req, 'data', req.json.get('data'))

    @staticmethod
    def setup_session(req):
        sid = req.identification.get('session_id')
        if sid:
            req.session = session_mgr.get(sid)
        else:
            req.session = session_mgr.new()

    @staticmethod
    def fix_lang(req):
        assert req.session
        lang = req.data.get('lang')
        if lang:
            if lang.find('zh') > -1:
                req.session.context['lang'] = 'zh_CN'
            elif lang.find('en') > -1:
                req.session.context['lang'] = 'en_US'

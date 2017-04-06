try:
    import ujson as json
except ImportError:
    import json

from collections import defaultdict

from sanic.exceptions import SanicException


class BaseExcep(Exception):
    def __init__(self, *args, msg='', code=1, data={}, log=False, **kwargs):
        self.code = code
        self.data = data
        self.msg = msg
        self.log = log
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return json.dumps({
            "code": self.code,
            "data": self.data,
            "msg": self.msg,
            "id": None
        })

    __str__ = __repr__


class LoginError(SanicException):
    status_code = 110
    msg = defaultdict(lambda: 'Wrong login/password!', {
        'en_US': 'Wrong login/password!',
        'zh_CN': '用户名或密码错误！'
    })
    reason = None

    def __init__(self, code=None, message=None, reason=None):
        if message and message:
            self.message = message
        else:
            self.message = self.msg

        if code and isinstance(code, int):
            self.code = code
        else:
            self.code = self.status_code
        if reason:
            self.reason = reason
        super(LoginError, self).__init__(message=self.message,
                                         status_code=self.code)


class NoPwdError(LoginError):
    status_code = 111
    msg = 'no password'


class PwdRetryLimitError(LoginError):
    status_code = 113
    msg = defaultdict(lambda: 'retry limit', {
        'zh_CN': '工资单密码错误',
        'en_US': 'Wrong password'
    })


class WrongPwdError(LoginError):
    status_code = 112
    msg = defaultdict(lambda: 'Wrong password', {
        'zh_CN': '工资单密码错误',
        'en_US': 'Wrong password'
    })


class SecurityStrategyError(SanicException):
    status_code = 120
    msg = defaultdict(lambda: 'Security Strategy Error', {
        'zh_CN': '安全策略错误',
        'en_US': 'Security Strategy Error'
    })
    reason = None

    def __init__(self, code=None, message=None, reason=None):
        if message:
            self.message = message
        else:
            self.message = self.msg

        if code and isinstance(code, int):
            self.code = code
        else:
            self.code = self.status_code
        if reason:
            self.reason = reason
        super(SecurityStrategyError, self).__init__(message=self.message,
                                                    status_code=self.code)


class SessionExpiredError(SecurityStrategyError):
    status_code = -5
    msg = defaultdict(lambda: 'Session expired. Please retry', {
        'zh_CN': '会话过期，请重新登录',
        'en_US': 'Session expired. Please retry'
    })


class PreventAppError(SecurityStrategyError):
    status_code = 121
    msg = defaultdict(lambda: 'Your are not allowed to login via APP', {
        'zh_CN': '您未被允许使用APP登录',
        'en_US': 'Your are not allowed to login via APP'
    })


class ForceChgpwError(SecurityStrategyError):
    status_code = 303
    msg = defaultdict(lambda: 'Please change your password', {
        'zh_CN': '请修改密码',
        'en_US': 'Please change your password'
    })


class PwdLockError(SecurityStrategyError):
    status_code = 123
    msg = defaultdict(
        lambda: 'Your password has been locked. Please contact system admin', {
            'zh_CN': '您的密码被锁定，请联系管理员',
            'en_US': 'Your password has been locked. Please contact system admin'
        })


class UserLockError(SecurityStrategyError):
    status_code = 124
    msg = defaultdict(
        lambda: 'You are not allowed login, please contact Admin to unlock!', {
            'zh_CN': '你已经被锁定, 请联系管理员解锁!',
            'en_US': 'You are not allowed login, please contact Admin to unlock!'
        })

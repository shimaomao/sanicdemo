import logging
from decimal import Decimal, ROUND_HALF_UP

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger('')


class FrozenDict(dict):
    """ An implementation of an immutable dictionary. """

    def __delitem__(self, key):
        raise NotImplementedError("'__delitem__' not supported on frozendict")

    def __setitem__(self, key, val):
        raise NotImplementedError("'__setitem__' not supported on frozendict")

    def clear(self):
        raise NotImplementedError("'clear' not supported on frozendict")

    def pop(self, key, default=None):
        raise NotImplementedError("'pop' not supported on frozendict")

    def popitem(self):
        raise NotImplementedError("'popitem' not supported on frozendict")

    def setdefault(self, key, default=None):
        raise NotImplementedError("'setdefault' not supported on frozendict")

    def update(self, *args, **kwargs):
        raise NotImplementedError("'update' not supported on frozendict")

    def __hash__(self):
        return hash(
            frozenset((key, hash(val)) for key, val in self.iteritems()))


def dict_num_sum(value):
    """
    对字典进行合计
    :param value:
    :return:
    """
    if not value:
        return 0.0

    if isinstance(value, dict):
        total = 0
        for value1 in value.values():
            value1 = dict_num_sum(value1)
            total += value1
        return total
    else:
        try:
            value = float(value)
        except Exception as e:
            logger.exception(e)
            value = 0.0
        return value


def decimal_round(number, precision):
    '''
    @param number: 数值
    @param precision: 精度处理位数
    @return: 对数值进行四舍五入, precision 为其保留的位数, 采用decimal是为了防止float值 十进制转换为二进制时所造成的误差造成四舍五入出现错误
    '''
    # 兼容 '' None 等空值
    if not number and number != 0:
        return decimal_round(0, precision)

    if isinstance(number, (float, int)):
        # precision不能为负
        if precision < 0:
            return number
        number = repr(number)

    try:
        precision_str = 1 if precision == 0 else '0.' + '0' * (
            precision - 1) + '1'
        # result为 decimal值,ROUND_HALF_UP 四舍五入, precision_str为精度
        result = Decimal(number).quantize(Decimal(precision_str),
                                          rounding=ROUND_HALF_UP)
    except Exception as e:
        logger.exception(e)
        return decimal_round(0, precision)

    return result


def get_formative_money(money, precision=2):
    """
    按精度四舍五入
    增加千位符

    按精度保留小数 位数
    0 处理为 0.00
    100 处理为 100.00
    """
    return "{:,}".format(decimal_round(money, precision))


def delete_zero(value, code='', dict1={}):
    '''
    删除字典中的0值  张海洋代码,未修改
    :param value:
    :param code:
    :param dict1:
    :return:
    '''
    if isinstance(value, dict):
        for code1, value1 in value.items():
            value1 = delete_zero(value1, code1, value)
            try:
                value1 = float(value1)
                if value1 == 0:
                    value.pop(code1)
            except:
                pass
        if dict1.get(code) == {}:
            dict1.pop(code)
    else:
        return value

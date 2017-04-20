from structure.model import SalaryModel
from .environment import Environment


all_model = {'salary':SalaryModel}


class ModelDict(dict):

    def __init__(self, service):
        super(ModelDict, self).__init__()
        self.service = service

    def __getitem__(self, y):
        try:
            model = super(ModelDict, self).__getitem__(y)
        except KeyError:
            model = self.service.import_model(y)

        return model





class BaseService:

    def __init__(self, env, connection=None):
        self.env = env
        self.model = ModelDict(self)

    def import_model(self, name):
        model_cls = all_model.get(name)
        if model_cls:
            model = model_cls(self.env)
            self.model[name] = model
        else:
            raise (KeyError, 'no model named {} in service.py'.format(name))
        return model
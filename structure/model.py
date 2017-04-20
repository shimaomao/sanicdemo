from base.model import BaseModel
import random



class SalaryModel(BaseModel):

    def data_format(self, data, show_id=True):

        data_list = []
        if show_id:
            [data_list.append({'code': item['code'], 'name':item['name_zh'].strip()}) for item in data if item]
        else:
            [data_list.append(item['name_zh'].strip()) for item in data if item]
        return data_list

    async def get_all_city(self, show_id=False):

        data = await self.db.find('city', 'list', {})
        city_list = self.data_format(data,show_id)

        return city_list

    async def get_all_industry(self, show_id=False):
        data = await self.db.find('industry', 'list', {})
        category_list = self.data_format(data, show_id)

        return category_list

    async def get_all_scope(self, show_id=False):
        data = await self.db.find('company_scope', 'list', {})
        scope_list = self.data_format(data, show_id)
        return scope_list

    async def get_all_nature(self, show_id=False):
        data = await self.db.find('company_scope', 'list', {})
        nature_list = self.data_format(data, show_id)
        return nature_list

    async def get_dep_cate_mapping(self):
        data = await self.db.find('x_department as dep', 'list', {
            'fields': ['dep.id', 'dep.name as dep_name', 'cate.name as cate_name', 'category_id'],
            'join': 'x_category as cate on cate.id = dep.category_id'
        })
        mapping_dict = {}
        for item in data:
            if item['category_id'] in mapping_dict:
                mapping_dict[item['category_id']].append({item['id']: item['dep_name'].strip()})
            else:
                mapping_dict[item['category_id']] = [{item['id']: item['dep_name'].strip()}]
        return mapping_dict

    async def get_job_cate_mapping(self):
        data = await self.db.find('job', 'list', {
            'fields': ['job.code', 'job.name_zh', 'cate.name_zh as category_name', 'job_category_code'],
            'join': 'job_category as cate on cate.code = job.job_category_code'
        })
        job_list = []
        mapping_dict = {}
        job_category_name_mapping = {}
        for item in data:
            if item['job_category_code'] in mapping_dict:
                mapping_dict[item['job_category_code']].append({'code': item['code'], 'name': item['name_zh'].strip()})
            else:
                mapping_dict[item['job_category_code']] = [{'code': item['code'], 'name': item['name_zh'].strip()}]
                job_category_name_mapping[item['job_category_code']] = item['category_name']
        for k, v in mapping_dict.items():
            job_list.append({'code': k, 'name': job_category_name_mapping.get(k), 'jobs': v})
        return job_list

    async def get_all_rank(self, show_id):
        data = await self.db.find('job_grade', 'list', {})
        rank_list = self.data_format(data, show_id)
        return rank_list

    async def get_job_by_cate_rank(self, category_code, rank_code):
        data = await self.db.find('job', 'list', {
            'condition': 'job_category_code={} and job_grade_code={}'.format(category_code, rank_code),
        })
        data_list = []
        [data_list.append({'code': item['code'], 'name':item['name_zh'].strip(),
                           'market_50':random.randint(10000, 20000)}) for item in data if item]
        return data_list

    async def get_job_info_by_name(self, name_list):
        condition = ''
        if isinstance(name_list, list or tuple):
            if len(name_list) > 1:
                condition = 'job.name_zh in {}'.format(str(tuple(name_list)))

        else:
            condition = 'job.name_zh = {}'.format(name_list)

        data = await self.db.find('job', 'list', {
            'condition': condition,
            'fields': ['job.*, job_category.name_zh as job_category_name, job_grade.name_zh as job_grade_name'],
            'join': 'job_category on job_category.code = job.job_category_code left join job_grade on job_grade.code = job.job_grade_code'
        })

        return data



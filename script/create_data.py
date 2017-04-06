# --*-- coding:utf-8 --*--
import xlrd
import uuid
import random
import logging

CITY_LIST = ['北京', '上海', '天津', '重庆', '广州', '深圳', '杭州', '苏州', '成都', '西安', '大连', '沈阳', '珠海']
CATEGORY_LIST = set()
DEP_DICT = {}
JOB_DICT = {}
GRADE_LIST = []
TIME_LIST = []

work_table = xlrd.open_workbook('/Users/panyang/Documents/市场数据库_样本数据.xlsx')
salary_page = 0
para_page = 1
structure_page = 2
code_set = set()
job_mapping = {}
industry_mapping = {}
print(CATEGORY_LIST, DEP_DICT, JOB_DICT)
logging.getLogger().setLevel(logging.INFO)

def gen_code():

    while True:
        code = random.randint(1000, 9999)
        if code not in code_set:
            code_set.add(code)
            return code

async def read_structure(pool):

    job_grade_set = set()
    job_category_set = set()
    job_category_mapping = {}
    job_grade_mapping = {}
    structure_table = work_table.sheet_by_index(structure_page)
    for row in range(1, structure_table.nrows):
        one_structure = structure_table.row_values(row)
        job_grade_set.add(one_structure[2])
        job_category_set.add(one_structure[1])

    async with pool.acquire() as conn:
        for job_category in job_category_set:
            code = gen_code()
            job_category_mapping[code] = job_category
            job_category_mapping[job_category] = code

            await conn.execute('insert into JOB_CATEGORY (CODE, NAME_ZH) VALUES ( \'{}\', \'{}\')'.format(code, job_category))

    async with pool.acquire() as conn:
        for job_grade in job_grade_set:
            code = gen_code()
            job_grade_mapping[code] = job_grade
            job_grade_mapping[job_grade] = code
            await conn.execute('insert into JOB_GRADE (CODE, NAME_ZH) VALUES ( \'{}\',  \'{}\')'.format(code, job_grade))

    async with pool.acquire() as conn:
        for row in range(1, structure_table.nrows):
            one_structure = structure_table.row_values(row)
            code = gen_code()
            job = one_structure[0]
            job_mapping[code] = job
            job_mapping[job] = code
            job_category_code = job_category_mapping[one_structure[1]]
            job_grade_code = job_grade_mapping[one_structure[2]]
            await conn.execute('insert into JOB (CODE, NAME_ZH, JOB_GRADE_CODE, JOB_CATEGORY_CODE) '
                               'VALUES ( \'{}\',  \'{}\', \'{}\',  \'{}\')'.format(code, job, job_grade_code, job_category_code))

async def create_city(pool):
    async with pool.acquire() as conn:
        for item in CITY_LIST:
            await conn.execute('insert into CITY (NAME_ZH, code) VALUES ({}, {})'.format('\'' + item + '\'', gen_code()))


async def create_nature_and_scope(pool):
    print(gen_code())
    print(gen_code())
    print(gen_code())

async def create_industry(pool):

    para_table = work_table.sheet_by_index(para_page)

    async with pool.acquire() as conn:
        for row in range(1, 28):
            one_structure = para_table.row_values(row)
            name = one_structure[0]
            code = gen_code()
            industry_mapping[name] = code
            industry_mapping[code] = name
            await conn.execute('insert into INDUSTRY (NAME_ZH, CODE) VALUES (\'{}\',  \'{}\')'.format(name, code))

async def create_salary(pool):
    salary_table = work_table.sheet_by_index(salary_page)
    logging.info('start create data')
    async with pool.acquire() as conn:
        await conn.execute('TRUNCATE TABLE market_salary_data')
        for row in range(2, salary_table.nrows):
            one_structure = salary_table.row_values(row)
            job_code = job_mapping[one_structure[0]]
            industry_code = industry_mapping[one_structure[1]]
            city_code = 8308
            scope_code = 8010
            nature_code = 7164
            source = 'eraod'
            for i in range(5, 104):
                salary = one_structure[i]
                await conn.execute('insert into market_salary_data (SOURCE, city_code, job_code, industry_code, scope_code'
                                   ', nature_code, base_salary) VALUES (\'{}\', {}, {},{}, {},{}, {})'.format(source,city_code,job_code,industry_code, scope_code,nature_code, salary))
            logging.info('finish line {}'.format(row))

async def create_data(pool):

    #await create_city(pool)
    await create_industry(pool)
    await create_nature_and_scope(pool)
    await read_structure(pool)
    await create_salary(pool)


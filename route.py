from controller import CityList, CategoryList, CateDepMapping, DepJobMapping, CompanyDetail, SalaryData
from middlemare import success


route = {
    '/get_all_city': CityList,
    '/get_all_category': CategoryList,
    '/get_department_mapping': CateDepMapping,
    '/get_job_mapping': DepJobMapping,
    '/get_company_detail': CompanyDetail,
    '/upload_excel': SalaryData
}

middleware = {
    'response': [success]
}

err_route = {}
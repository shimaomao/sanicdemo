from structure.controller import GetBaseInfo, GetJobInfo, GetJobByCateAndRank, JobMapping
from structure.middlemare import success, log


route = {

    '/get_base_info': GetBaseInfo,
    '/get_job_info': GetJobInfo,
    '/get_job_by_cate_and_rank': GetJobByCateAndRank,
    '/job_mapping': JobMapping
}

middleware = {
    'request':  [log],
    'response': [success]
}

err_route = {}
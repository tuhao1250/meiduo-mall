from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """美多商城标准分页器类"""
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 20

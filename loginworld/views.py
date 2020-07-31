from django.shortcuts import render
from django.contrib.auth.decorators import permission_required


# Create your views here.


@permission_required('users.add_users')
def add_user_html(request):
    if request.method == 'GET':
        return HttpResponse('当前用户无法添加新用户')
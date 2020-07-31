

def user_permission(request):
    if request.method == 'GET':
        # 获取id=1d的用户对象
        user = Users.objects.get(id=1)
        # 查看用户的所有权限
        all_perm = user.get_all_permissions()
        # 查看用户的组权限
        group_perm = user.get_group_permissions()
        # 查询用户是否有add_user_per权限
        if user.has_perm('users.add_user_per'):
            return HttpResponse('用户有add_user_per权限')
        else:
            return HttpResponse('用户没有add_user_per权限')
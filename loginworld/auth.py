from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User


# 用户登陆
user = authenticate(username, password)
if user:
    if user.is_active:
        login(request, user)
    else:
        print('账号密码错误')
else:
    print("登陆失败")
# 注销
logout(request)

# 创建用户
user = User.objects.create_user(username, password)
user.savae()
# 修改密码
user = authenticate(username, password)
user.set_password(new_password)
user.save()

# 对密码加密和检查加密前的密码和加密后的密码是否相等
from django.contrib.auth.hashers import make_password, check_password

password = "123456"
code_password = make_password(password, None, "pbkdf2_sha256")
check_password(password, code_password)
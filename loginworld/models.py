from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

# 编写模型管理器

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status="published")

# 每个模型至少一个管理器，默认使用objects
# 通过一个模型管理，可以得到一个Queryset
class adminter(models.Model):
    STATUS_CHOICES = (("normal", "正常"),("delete", "删除"))
    # 为了生成唯一表示的ID
    ID = models.SlugField(max_length=50, primary_key=True)
    name = models.CharField('姓名', max_length=30, unique=True, db_column='username')
    password = models.CharField('密码', max_length=8, db_column='password', help_text='请设置8位密码')
    # 设定一个参数控制权限
    flag = models.CharField(max_length=10)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES, default="normal")
    # 邮箱为可选项，blank进行控制
    email = models.CharField('邮箱', max_length=40, blank=True, null=True)

    class Meta:
        db_table = "adminter"
        verbose_name = verbose_name_plural = "系统人员信息"
        ordering = ("ID")
        permissions = (
            ('add_user_per', '添加用户权限'),
            ('del_user_per', '删除用户权限'),
            ('change_user_per', '修改用户权限'),
            ('sel_user_per', '查询用户权限')
        )
    def __str__(self):
        return self.name

    objects = models.Manager()  # 默认的管理器
    published = PublishedManager()  # 自定义管理器

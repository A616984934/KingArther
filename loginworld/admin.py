from django.contrib import admin
from loginworld.models import adminter
# Register your models here.


@admin.register()
class PostAdmin(admin.ModelAdmin):
    # admin.register 用于将PostAdmin类注册成Post的管理类
    # list_display 属性将指定哪些字段在详情页中显示出来
    list_display = ("title", "slug", "author", "publish", "status")
    list_filter = ("status", "created", "publish", "author")
    search_fields = ("title", "body")
    # prepopulated_fields 属性中slug字段与title字段的对应关系
    prepopulated_fields = {"slug": ('title',)}


@admin.register(adminter)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "ID", "", "created", "active")
    list_filter = ("active", "created", "updated")
    search_fields = ("name", "email", "body")

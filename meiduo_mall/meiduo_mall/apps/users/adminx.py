import xadmin
from xadmin.plugins import auth
from users.models import User


class UserAdmin(auth.UserAdmin):
    """使用自定义的用户模型类"""
    list_display = ('id', 'username', 'mobile', 'email', 'date_joined', 'is_staff')
    read_only_fields = ['last_login', 'date_joined']
    search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile')
    style_fields = {'user_permissions': 'm2m_transfer', 'groups': 'm2m_transfer'}

    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            # 表示是新建的表单的时候
            self.fields = ['username', 'mobile', 'is_staff']

        return super().get_model_form(**kwargs)


xadmin.site.unregister(User)
xadmin.site.register(User, UserAdmin)
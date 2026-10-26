from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil & Rôle'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')

    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return "-"
    get_role.short_description = 'Rôle CargoLink'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user = form.instance
        if hasattr(user, 'profile'):
            user.profile.save()



# Réenregistre User avec le profil inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'entreprise', 'telephone', 'date_creation')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'entreprise', 'telephone')


from types import MethodType
from django.shortcuts import render

def custom_admin_login(self, request, extra_context=None):
    context = {
        'page_title': 'Page Non Accessible • CargoLink',
        'current_user': request.user if (request.user and request.user.is_authenticated) else None,
    }
    return render(request, 'accounts/admin_access_denied.html', context, status=403)

def custom_has_permission(self, request):
    if not request.user.is_active or not request.user.is_authenticated:
        return False
    if request.user.is_superuser or request.user.is_staff:
        return True
    if hasattr(request.user, 'profile') and request.user.profile.is_admin:
        return True
    return False

admin.site.login = MethodType(custom_admin_login, admin.site)
admin.site.has_permission = MethodType(custom_has_permission, admin.site)


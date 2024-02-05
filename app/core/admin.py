"""
Django admin customization.
"""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from cloudinary.forms import CloudinaryFileField

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login', )}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Category)


class ProductAdminForm(forms.ModelForm):
    # Using Cloudinary's file field for the image
    image = CloudinaryFileField(
        options={
            'folder': 'product_images',
            'overwrite': True,
            'resource_type': 'image'
        },
        required=False
    )

    class Meta:
        model = models.Product
        fields = '__all__'


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'price', 'stock', 'category', 'user', 'image_tag']
    readonly_fields = ['image_tag']

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" />',
                               obj.image.url)
        return "No Image Uploaded"
    image_tag.short_description = 'Image'

    fields = ('name', 'description', 'price',
              'stock', 'category', 'user', 'image')

    # Adjust the fields and fieldsets as per your requirements
    fields = ('name', 'description', 'price',
              'stock', 'category', 'user', 'image')


admin.site.register(models.Order)
admin.site.register(models.OrderItem)
admin.site.register(models.Cart)
admin.site.register(models.CartItem)

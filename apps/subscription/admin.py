from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import Subscription, PromoConfig


@admin.register(PromoConfig)
class PromoConfigAdmin(ModelAdmin):
    list_display = ["is_active", "max_limit"]


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    change_list_template = "admin/subscription/subscription/change_list.html"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        promo_config = PromoConfig.get_solo()
        extra_context['promo_active'] = promo_config.is_active
        extra_context['promo_count'] = Subscription.objects.filter(is_promo=True).count()
        extra_context['promo_limit'] = promo_config.max_limit
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('toggle-promo/', self.admin_site.admin_view(self.toggle_promo), name='subscription_subscription_toggle_promo'),
        ]
        return custom_urls + urls

    def toggle_promo(self, request):
        if request.method == 'POST':
            promo_config = PromoConfig.get_solo()
            promo_config.is_active = not promo_config.is_active
            promo_config.save()
            return JsonResponse({'success': True, 'is_active': promo_config.is_active})
        return JsonResponse({'success': False}, status=400)
from django.contrib import admin
from .models import Customer,usefulSite,client,Team,testmony,Product,Orders,Feedback,Category,quote,subscribe
# Register your models here.

admin.site.register(Category)
admin.site.register(subscribe)
admin.site.register(testmony)
admin.site.register(Team)
admin.site.register(client)
admin.site.register(usefulSite)

class QuoteAdmin(admin.ModelAdmin):
    pass
admin.site.register(quote, QuoteAdmin)

class CustomerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Customer, CustomerAdmin)

class ProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(Product, ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    pass
admin.site.register(Orders, OrderAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feedback, FeedbackAdmin)
# Register your models here.

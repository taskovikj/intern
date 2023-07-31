from django.contrib import admin

from .models import Listing,User,Category,BiddingLogg,PageVisited

admin.site.register(Listing)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(BiddingLogg)
admin.site.register(PageVisited)



# Register your models here.

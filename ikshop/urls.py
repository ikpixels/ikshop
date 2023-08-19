from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django .conf.urls. static import static
from django .conf import settings
from django.conf.urls import handler404, handler500
from django.contrib.auth.views import LoginView,LogoutView

from django.contrib import admin
from django.urls import path
from shop import views
from django.contrib.auth.views import LoginView,LogoutView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name=''),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('shop', views.shop_view,name='shop'),
    path('mysite',views.mysite,name="mysite"),
    path('shop/<Cate>/', views.shop_view,name='cate'),

    path('pricing',views.pricing,name='pricing'),
    path('pricing2',views.pricing2,name='pricing2'),
    path('pricing3',views.pricing3,name='pricing3'),

    path('webdesign', views.webdesign_view,name='webdesign'),
    path('webdev', views.webdev_view,name='webdev'),
    path('graphics', views.graphics_view,name='graphics'),
    path('hosting', views.hosting_view,name='hosting'),
    path('business', views.busines_view,name='busines'),

    path('gallary', views.gallary_view,name='gallary'),
    path('work-detail/<slug>/',views.gallary_detail_view,name="work-detail"),
    path('shop-detail/<slug>/', views.shop_detail_view,name='shop_detail'),
    path('logout', LogoutView.as_view(template_name='ik/logout.html'),name='logout'),
    path('aboutus', views.aboutus_view,name='aboutus'),
    path('contactus', views.contactus_view,name='contactus'),
    path('search', views.search_view,name='search'),
    path('send-feedback', views.send_feedback_view,name='send-feedback'),
    path('view-feedback', views.view_feedback_view,name='view-feedback'),

    path('adminclick', views.adminclick_view),
    path('adminlogin', LoginView.as_view(template_name='ikpixels/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

    path('view-customer', views.view_customer_view,name='view-customer'),
    path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),
    path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),

    path('admin-products', views.admin_products_view,name='admin-products'),
    path('admin-add-product', views.admin_add_product_view,name='admin-add-product'),
    path('delete-product/<int:pk>', views.delete_product_view,name='delete-product'),
    path('update-product/<int:pk>', views.update_product_view,name='update-product'),

    path('admin-view-booking', views.admin_view_booking_view,name='admin-view-booking'),
    path('delete-order/<int:pk>', views.delete_order_view,name='delete-order'),
    path('update-order/<int:pk>', views.update_order_view,name='update-order'),


    path('customersignup', views.customer_signup_view),
    path('customerlogin', LoginView.as_view(template_name='ik/customerlogin.html'),name='customerlogin'),
    path('customer-home', views.customer_home_view,name='customer-home'),
    path('my-order', views.my_order_view,name='my-order'),
    # path('my-order', views.my_order_view2,name='my-order'),
    path('my-profile', views.my_profile_view,name='my-profile'),
    path('edit-profile', views.edit_profile_view,name='edit-profile'),
    path('download-invoice/<int:orderID>/<int:productID>', views.download_invoice_view,name='download-invoice'),


    path('add-to-cart/<int:pk>', views.add_to_cart_view,name='add-to-cart'),
    path('cart', views.cart_view,name='cart'),
    path('remove-from-cart/<int:pk>', views.remove_from_cart_view,name='remove-from-cart'),
    path('customer-address', views.customer_address_view,name='customer-address'),
    path('payment-success', views.payment_success_view,name='payment-success'),


]

urlpatterns+=staticfiles_urlpatterns()
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


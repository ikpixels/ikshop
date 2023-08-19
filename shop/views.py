from django.shortcuts import render,redirect,reverse
from . import forms,models

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings

def MainMail(html_path,ctx,receiver,subject):

    body = get_template(html_path).render(ctx)
    msg = EmailMessage(subject,body,settings.EMAIL_HOST_USER,receiver)
    msg.content_subtype ="html"
    msg.send()

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def mainCart(request,context):
    # fetching product details from db whose id is present in cookie
    c_products=None
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            c_products=models.Product.objects.all().filter(id__in = product_id_in_cart)

            #for total price shown in cart
            for p in c_products:
                total=total+p.price

    context['c_products'] = c_products
    context['total'] = total

    #Cart on top notification
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    context['product_count_in_cart'] = product_count_in_cart



def home_view(request):

    context ={}

    mainCart(request,context)


    context['pj'] = models.Product.objects.filter(forsale=False)

    products=models.Product.objects.filter(forsale=True)
    context['products'] = products
    context['client'] = models.client.objects.all()
    context['testimony'] = models.testmony.objects.all()

    return render(request,'ik/ik-index.html',context)

def shop_view(request,Cate=None):

    context = {}

    mainCart(request,context)
    context['category'] = models.Category.objects.all()

    if Cate:
        Cate2 = models.Category.objects.get(name=Cate).id
        products =models.Product.objects.filter(forsale=True,category=Cate2)
    else:
        products =models.Product.objects.filter(forsale=True)

    page = request.GET.get('page', 1)
    paginator = Paginator(products,12)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context['products'] = products
    
    return render(request,'ik/shop.html',context)


def gallary_view(request):

    context = {}

    products =models.Product.objects.filter(forsale=False)

    page = request.GET.get('page', 1)
    paginator = Paginator(products,12)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context['products'] = products

    mainCart(request,context)

    context['category'] = models.Category.objects.all()[:5]
   
    return render(request,'ik/gallery.html',context)


def gallary_detail_view(request,slug):
    context = {}
    work= models.Product.objects.get(forsale=False,slug=slug)
    context['work']  = work
    context['products'] = models.Product.objects.filter(forsale=False,category=work.category)
    return render(request,'ik/gallery_detail.html',context)

def shop_detail_view(request,slug):

    context = {}

    product =models.Product.objects.get(slug=slug)
    context['p'] = product

    products =models.Product.objects.filter(forsale=True,category=product.category)
    context['products'] = products #featured products

    mainCart(request,context)

    context['category'] = models.Category.objects.all()
   
    return render(request,'ik/shop-detail.html',context)



#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def customer_signup_view(request):

    context = {}

    mainCart(request,context)

    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()


    context['userForm'] = userForm
    context['customerForm'] = customerForm

    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)


            get_email = request.POST['email']
            full_name = request.POST['first_name']+' '+request.POST['last_name']
            
            ctx ={'name':full_name}
            
            subject = 'You have created customer account'
            message2 = get_template('email/acount_mail.html').render(ctx)
            msg = EmailMessage( subject,
                                message2,
                                settings.EMAIL_HOST_USER,
                                [get_email])
            msg.content_subtype ="html"
            msg.send()


        return HttpResponseRedirect('customerlogin')

        

    return render(request,'ik/customersignup.html',context)

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):

    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):

    context = {}

    mainCart(request,context)


    context['pending'] = models.Orders.objects.filter(status='Pending').count()
    context['OrderConfirmed'] = models.Orders.objects.filter(status='Order Confirmed').count()
    context['OutforDelivery'] = models.Orders.objects.filter(status='Out for Delivery').count()
    context['Delivered'] =  models.Orders.objects.filter(status='Delivered').count()

    # for cards on dashboard
    customercount=models.Customer.objects.all().count()
    productcount=models.Product.objects.all().count()
    ordercount=models.Orders.objects.all().count()

    # for recent order tables
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

   
    context['customercount'] =customercount
    context['productcount'] =productcount 
    context['ordercount'] = ordercount
    context['data'] = zip(ordered_products,ordered_bys,orders)

    return render(request,'admin1/index.html',context)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):

    context = {}
    mainCart(request,context)
    context['customers']=models.Customer.objects.all()

    return render(request,'admin1/customer.html',context)

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):

    context = {}

    mainCart(request,context)

    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)

    context['userForm'] = userForm
    context['customerForm'] = customerForm

    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')

    return render(request,'admin1/update_customer.html',context)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):

    context = {}

    mainCart(request,context)

    context['products'] =models.Product.objects.all()
    return render(request,'admin1/admin_products.html',context)


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):

    context = {}

    mainCart(request,context)

    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')

    context['productForm'] = productForm

    return render(request,'ik/admin_add_products.html',context)


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):

    mainCart(request,context)

    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):

    context = {}

    mainCart(request,context)

    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')

    context['productForm'] = productForm
    return render(request,'admin1/admin_update_product.html',context)


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):

    context = {}



    mainCart(request,context) 

    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    context['data'] = zip(ordered_products,ordered_bys,orders)
    return render(request,'admin1/admin_view_booking.html',context)


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):

    context = {}

    mainCart(request,context)

    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')

    context['orderForm'] = orderForm

    return render(request,'admin1/update_order.html',context)



@login_required(login_url='adminlogin')
def mysite(request):
    context = {}
    site = models.usefulSite.objects.all()
    context['site'] =site
    return render(request,'admin1/mysite.html',context)


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):

    context = {}

    mainCart(request,context)

    feedbacks=models.Feedback.objects.all().order_by('-id')

    context['feedbacks'] = feedbacks
    return render(request,'ecom/view_feedback.html',context)



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):

    context = {}

    mainCart(request,context)

    # whatever user write in search box we get in query
    query = request.GET['query']
    products=models.Product.objects.all().filter(name__icontains=query)
    

    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    context['search_p'] = products
    context['word'] = word
   

    if request.user.is_authenticated:
        return render(request,'ik/customer_home.html',context)
    return render(request,'ik/shop.html',context)


# any one can add product to cart, no need of signin
def add_to_cart_view(request,pk):

    context = {}

    products=models.Product.objects.filter(forsale=True)
    context['products'] = products

    mainCart(request,context)


    response = render(request, 'ik/customer_home.html',context)
    
    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
        
    else:
        response.set_cookie('product_ids', pk)
    product=models.Product.objects.get(id=pk)

    return response
   
# for checkout of cart
def cart_view(request):

    context = {}
    mainCart(request,context)
    return render(request,'ik/cart.html',context)


def remove_from_cart_view(request,pk):

    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # removing product id from cookie
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart=product_ids.split('|')
        product_id_in_cart=list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products=models.Product.objects.all().filter(id__in = product_id_in_cart)
        #for total price shown in cart after removing product
        for p in products:
            total=total+p.price

        #  for update coookie value after removing product id in cart
        value=""
        for i in range(len(product_id_in_cart)):
            if i==0:
                value=value+product_id_in_cart[0]
            else:
                value=value+"|"+product_id_in_cart[i]
        response = render(request, 'ik/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})
        if value=="":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids',value)
        return response


def send_feedback_view(request):

    context = {}
    mainCart(request,context)

    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    context['feedbackForm']=feedbackForm
    return render(request, 'ecom/send_feedback.html',context)


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request,cate=None):

    context = {}

    mainCart(request,context)

    
    products=models.Product.objects.filter(forsale=True)[:12]

    context['products'] = products

    context['category'] = models.Category.objects.all()

    return render(request,'ik/customer_home.html',context)



# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    context = {}
    mainCart(request,context)
    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of order placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile=addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            #for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
            total=0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids != "":
                    product_id_in_cart=product_ids.split('|')
                    products=models.Product.objects.all().filter(id__in = product_id_in_cart)
                    for p in products:
                        total=total+p.price

            context['total'] = total
            
            response = render(request, 'ik/payment.html',context)
            response.set_cookie('email',email)
            response.set_cookie('mobile',mobile)
            response.set_cookie('address',address)

            return response

    context['addressForm'] = addressForm



    return render(request,'ik/customer_address.html',context)




# here we are just directing to this view...actually we have to check whther payment is successful or not
#then only this view should be accessed
@login_required(login_url='customerlogin')
def payment_success_view(request):

    context = {}

    mainCart(request,context)

    # Here we will place order | after successful payment
    # we will fetch customer  mobile, address, Email
    # we will fetch product id from cookies then respective details from db
    # then we will create order objects and store in db
    # after that we will delete cookies because after order placed...cart should be empty
    customer=models.Customer.objects.get(user_id=request.user.id)
    products=None
    email=None
    mobile=None
    address=None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)
            # Here we get products list that will be ordered by one customer at a time

    # these things can be change so accessing at the time of order...
    if 'email' in request.COOKIES:
        email=request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile=request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address=request.COOKIES['address']


    if request.method == 'POST':
        acountName = request.POST['name']
        pytMethod = request.POST['mobile']
        reference = request.POST['reference']
        amount = request.POST['amount']
   
    # here we are placing number of orders as much there is a products
    # suppose if we have 5 items in cart and we place order....so 5 rows will be created in orders table
    # there will be lot of redundant data in orders table...but its become more complicated if we normalize it
    for product in products:
        models.Orders.objects.get_or_create(customer=customer,amount=amount,
                                            product=product,status='Pending',
                                            email=email,mobile=mobile,
                                            address=address,pytMethod=pytMethod,
                                            reference=reference,
                                            accountName=acountName)
    URL = request.META['HTTP_HOST']#geting domain name

    #Sending Mail to customer after payment
    html_path = 'email/customer-payment.html'
    mail_ctx = {'customer':customer,'amount':amount,'pymt':pytMethod,'url':URL}
    receiver = [email,]
    subject = "Payment done!!"
    MainMail(html_path,mail_ctx,receiver,subject)

    #Sending mail to admin after payment
    html_path2 = 'email/admin-payment.html'
    mail_ctx2 = {'customer':customer,'amount':amount,'pymt':pytMethod,'acc':acountName,'ref':reference,'url':URL}
    receiver2 = ['kakodwaisaac@gmail.com',]
    subject2 = "Products Payment"
    MainMail(html_path2,mail_ctx2,receiver2,subject2)

    # after order placed cookies should be deleted
    response = render(request,'ik/payment_success.html',context)
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):

    context = {}

    mainCart(request,context)
    
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    context['data'] = zip(ordered_products,orders)

    return render(request,'ik/my_order.html',context)
 


#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request,orderID,productID):

    context = {}

    mainCart(request,context)

    order=models.Orders.objects.get(id=orderID)
    product=models.Product.objects.get(id=productID)
  
    context['orderDate'] = order.order_date
    context['customerName'] = request.user
    context['customerEmail'] = order.email
    context['customerMobile'] = order.mobile
    context['shipmentAddress'] = order.address
    context['orderStatus'] = order.status

    context['productName'] = product.name
    context['productImage'] = product.product_image
    context['productPrice'] = product.price
    context['productDescription'] = product.description

    return render_to_pdf('ik/download_invoice.html',context)

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ik/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):

    context = {}

    mainCart(request,context)

    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)

    context['userForm'] = userForm
    context['customerForm'] = customerForm
  
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ik/edit_profile.html',context)



#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    context = {}
    mainCart(request,context)


    context['team'] = models.Team.objects.all()
    context['client'] = models.client.objects.all()

    if is_ajax(request):
        Email = request.POST['Email']

        try:
            mail = models.subscribe.objects.filter(email=Email)

            if mail:
                info = "Already subscribe"
            else:
                info = "not subscribe"
                subs = models.subscribe(email=Email)
                subs.save()

                ctx ={'email':Email}

                subject = 'ikpixels - NewsLatter'
                message2 = get_template('admin1/subscribe.html').render(ctx)
                msg = EmailMessage( subject,
                            message2,
                            settings.EMAIL_HOST_USER,
                            [Email])
                msg.content_subtype ="html"
                msg.send()
                
        except models.subscribe.DoesNotExist:
            pass

    return render(request,'ik/about.html',context)

def contactus_view(request):
    context = {}

    mainCart(request,context)

    if is_ajax(request):
        name  = request.POST['name']
        phone = request.POST['phone']
        email = request.POST['email']
        subject = request.POST['subject']
        body    = request.POST['body']

        message = str(name)+' || '+str(email) +' || '+str(phone) + "\n" + body

        form = models.quote(name=name,phone=phone,email=email,Subject=subject,body=body)
        form.save()

        ctx = {'body':body,
               'subject':subject,
               'phone':phone,
               'name':name,
               'email':email,
              }

        message2 = get_template('ik/email.html').render(ctx)
        msg = EmailMessage( subject,
                            message2,
                            settings.EMAIL_HOST_USER,
                            ['kakodwaisaac@gmail.com'])

        msg.content_subtype ="html"# Main content is now text/html
        msg.send()

        

        
    return render(request, 'ik/contact-us.html',context)

#Services

def webdesign_view(request):
    context = {}
    mainCart(request,context)
    return render(request,'ik/webdesign.html',context)

def webdev_view(request):
    context = {}
    mainCart(request,context)
    return render(request,'ik/webdev.html',context)


def graphics_view(request):
    context = {}
    mainCart(request,context)
    return render(request,'ik/graphics.html',context)



def hosting_view(request):
    context = {}
    mainCart(request,context)
    return render(request,'ik/hosting.html',context)


def busines_view(request):
    context = {}
    mainCart(request,context)
    return render(request,'ik/busines.html',context)


def pricing(request):
    context = {}
    mainCart(request,context)
    return render(request,'ik/price.html',context)

def pricing2(request):
    context = {}
    mainCart(request,context)
    return render(request,'ik/price2.html',context)


def pricing3(request):
    context = {}
    mainCart(request,context)
    return render(request,'ik/price3.html',context)




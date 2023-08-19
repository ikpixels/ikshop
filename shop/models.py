from django.db import models
from django.contrib.auth.models import User

import datetime
import uuid
from django.db.models.signals import post_save,pre_save
from django.urls import reverse
from django.utils.text import slugify
# Create your models here.

TYPE = (
       ('My project','My project'),
       ('Useful site','Useful site')
    )
Work = (
      ('Django','Django'),
      ('Js','Js'),
      ('CSS','CSS'),
      ('Graphics','Graphics'),
      ('Mockup','Mockup'),
      ('HTM template','HTM template'),
      ('Python','Python'),
      ('Github','Github'),
      ('email','email'),
      ('source code','source code'),
      ('Others','Others'),
    )
class usefulSite(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100,choices=TYPE)
    work = models.CharField(max_length=100,choices=Work)
    url = models.URLField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    client = models.CharField(max_length=100,default ='none')

    def __str__(self):
        return self.name

class subscribe(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email

class client(models.Model):
    name = models.CharField(max_length=100,default='client')
    image= models.ImageField(upload_to='testmony_image/',null=True,blank=True)

    def __str__(self):
        return self.name

class testmony(models.Model):
    name = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    body = models.TextField()
    product_image= models.ImageField(upload_to='testmony_image/',null=True,blank=True)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    fb  = models.URLField(blank=True,null=True)
    tw  = models.URLField(blank=True,null=True)
    you = models.URLField(blank=True,null=True)
    gg  = models.URLField(blank=True,null=True)
    image= models.ImageField(upload_to='testmony_image/',null=True,blank=True)
    
    def __str__(self):
        return self.name

DISTRICT = (('Balaka','Balaka'),
            ('Blantyre','Blantyre'),
            ('Chikwawa','Chikwawa'),
            ('Chiradzuru','Chiradzuru'),
            ('Chitipa','Chitipa'),
            ('Dedza','Dedza'),
            ('Dowa','Dowa'),
            ('Karonga','Karonga'),
            ('Kasungu','Kasungu'),
            ('Likoma','Likoma'),
            ('Lilongwe','Lilongwe'),
            ('Machinga','Machinga'),
            ('Mangochi','Mangochi'),
            ('Mchinji','Mchinji'),
            ('Mulanje','Mulanje'),
            ('Mwanza','Mwanza'),
            ('Mzimba','Mzimba'),
            ('Neno','Neno'),
            ('Nkhata_Bay','Nkhata_Bay'),
            ('Nkhotakota','Nkhotakota'),
            ('Nsanje','Nsanje'),
            ('Ntcheu','Ntcheu'),
            ('Ntchisi','Ntchisi'),
            ('Phalombe','Phalombe'),
            ('Ruphi','Ruphi'),
            ('Salima','Salima'),
            ('Thyolo','Thyolo'),
            ('Zomba','Zomba'),
            ('Others','Others')
            )


class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name

class Category(models.Model):
    name=models.CharField(max_length=40)

    def __str__(self):
        return self.name



class Product(models.Model): #and artwork model
    name   =models.CharField(max_length=40)
    client =models.CharField(max_length=40,null=True,blank=True)
    link   = models.URLField(blank=True,null=True)
    district = models.CharField(max_length=100,choices=DISTRICT,blank=True,)
    category = models.ForeignKey(Category,null=True,blank=True,on_delete=models.CASCADE)
    slug     = models.SlugField(unique=True,null=True,blank=True)
    forsale   = models.BooleanField(default=False)
    product_image= models.ImageField(upload_to='product_image/',null=True,blank=True)
    product_image2= models.ImageField(upload_to='product_image/',null=True,blank=True)
    product_image3= models.ImageField(upload_to='product_image/',null=True,blank=True)
    price = models.DecimalField(max_digits=18, decimal_places=2,default=0)
    newprice = models.DecimalField(max_digits=18, decimal_places=2,default=0)
    description=models.CharField(max_length=40,null=True,blank=True)

    created_at        = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at        = models.DateTimeField(auto_now=True,null=True,blank=True)

    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('shop_detail',kwargs ={'slug':self.slug})

    def get_absolute_url2(self):
        return reverse('work-detail',kwargs ={'slug':self.slug})



def create_item_slug(instance,new_slug=None):
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
    qs = Product.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug,qs.first().id)
        return create_item_slug(instance,new_slug=new_slug)
    return slug

def pre_save_receiver_item(sender,instance,*args,**kwargs):
    if not instance.slug:
        instance.slug = create_item_slug(instance)

pre_save.connect(pre_save_receiver_item,sender=Product)


class Orders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
    product=models.ForeignKey('Product',on_delete=models.CASCADE,null=True)
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    order_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)

    amount = models.CharField(max_length=50,null=True,blank=True)

    pytMethod = models.CharField(max_length=50,null=True,blank=True)
    reference = models.CharField(max_length=50,null=True,blank=True)
    accountName = models.CharField(max_length=50,null=True,blank=True) 


class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name



class quote(models.Model):
    name =  models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    Subject = models.CharField(max_length=100)
    body = models.TextField()

    created_at        = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at        = models.DateTimeField(auto_now=True,null=True,blank=True)

    def __str__(self):
        return self.name

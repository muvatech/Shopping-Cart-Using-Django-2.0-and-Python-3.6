# Shopping-Cart-Using-Django-2.0-and-Python-3.6

Hey and welcome to this Python Django tutorial series. My name is Henry Mbugua
and I will be taking you through the various aspect of building a shopping cart application using Django 2.0
web framework and Python 3.6. I am a software developer at Muva Technologies where our main focus is to offer
services around mobile solutions(Apps), web solution
and websites, payments integration, web hosting and domains, and last but not least, consultancy and training.

> **Note:** the codebase has since been upgraded to run on **Django 5.2 LTS** and **Python 3.12+**. See the
> Setup section below for how to run it today.

## Setup (Django 5.2 LTS / Python 3.12+)

```powershell
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then edit DJANGO_SECRET_KEY for your own environment
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Topics that will be covered in this tutorial:

> **Note:** The original `muva.co.ke` blog is no longer online (the domain now
> redirects to an unrelated site). The links below point to Wayback Machine
> archives of the original posts instead.

Lesson 1 [Building an E-Commerce Shopping Cart Using Django 2.0 and Python 3.6 ](https://web.archive.org/web/20181001134115/http://muva.co.ke:80/blog/lesson-1-building-e-commerce-shopping-cart-using-django-2-0-python-3-6/)

Lesson 2 [Creating Our Shop app and designing product model in Django 2.0 and Python 3.6](https://web.archive.org/web/20181006075913/http://muva.co.ke:80/blog/creating-shop-app-designing-product-model-django-2-0-python-3-6/)

Lesson 3 [Registering our models in admin site and creating views in Django 2.0 and Python 3.6 ](https://web.archive.org/web/20181004164619/http://muva.co.ke:80/blog/lesson-3registering-models-admin-site-creating-views-django-2-0-python-3-6/)

Lesson 4 [Defining Url patterns and template for Our Shop products in Django 2.0 and Python 3.6](https://web.archive.org/web/20180428150602/http://muva.co.ke:80/blog/lesson-4-defining-url-patterns-template-shop-products-django-2-0-python-3-6/)

Lesson 5 [Completing product detail template for Our Shop products in Django 2.0 and Python 3.6 ](https://web.archive.org/web/20180916080834/http://muva.co.ke:80/blog/completing-product-detail-template-shop-products-django-2-0-python-3-6/)

Lesson 6 [Developing shopping cart class for Our Shop products in Django 2.0 and Python 3.6 ](https://web.archive.org/web/20180923231721/http://muva.co.ke:80/blog/developing-shopping-cart-class-shop-products-django-2-0-python-3-6/)

Lesson 7 [Creating Shopping Cart Views for Our Shop products in Django 2.0 and Python 3.6 ](https://web.archive.org/web/20180924162253/http://muva.co.ke:80/blog/creating-shopping-cart-views-shop-products-django-2-0-python-3-6/)

Lesson 8 [Developing a Context Processor for our Current Cart in Django 2.0 and Python 3.6 ](https://web.archive.org/web/20181001032910/http://muva.co.ke:80/blog/lesson-8-developing-context-processor-current-cart-django-2-0-python-3-6/)

Lesson 9 [Persisting customer orders to the database in Django 2.0 and Python 3.6](https://web.archive.org/web/20180823174435/http://muva.co.ke:80/blog/lesson-9-persisting-customer-orders-database-django-2-0-python-3-6/)

Lesson 10 [Lesson 10: Completing persisting customer orders to database in Django 2.0 and Python 3.6 ](https://web.archive.org/web/20180916082647/http://muva.co.ke:80/blog/lesson-10-completing-persisting-customer-orders-database-django-2-0-python-3-6/)

from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils.text import slugify
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50,unique=False)
    description = models.TextField(max_length=320)
    cat_image = models.ImageField(upload_to='photos/category',blank=True) 
    soft_deleted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Category'

    def __str__(self) -> str:
        return self.category_name


from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

#tuple for meals
MEALS = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner')
)

# Create your models here.
class Toy(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    #auto create cat_set for m:m
    def __str__(self):
        return f'{self.name}: {self.color}'
    def get_absolute_url(self):
        return reverse('toys_detail', kwargs={'pk':self.id})




class Cat(models.Model):
    name=models.CharField(max_length=100)
    breed=models.CharField(max_length=100)
    description=models.TextField(max_length=250)
    age=models.IntegerField()
    #add M:M
    toys = models.ManyToManyField(Toy)
        #add built in user model as fk to cat
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

    
    #redirect method for update and create
    def get_absolute_url(self):
        return reverse('detail', kwargs={'cat_id':self.id})

class Feeding(models.Model):
    date = models.DateField('feeding date')
    meal = models.CharField(
        max_length=1,
        # use choices from model field
        choices=MEALS,
        default=MEALS[0][0]
        )
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)
    def __str__(self):
        #get_meal_display() built in with Field.choice
        return f'{self.get_meal_display()} on {self.date}'
    class Meta:
        ordering = ['-date']

## use s3 to add photo start with model
class Photo(models.Model):
    url = models.CharField(max_length=200)
    cat =  models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f'Photo for cat_id: {self.cat_id} @{self.url}'





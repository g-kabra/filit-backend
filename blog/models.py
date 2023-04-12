from django.db import models

# Create your models here.

STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class blogModel(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, primary_key=True)
    read_time = models.IntegerField() # in minutes
    author = models.CharField(max_length=50, null=True, blank=True)
    content = models.TextField()
    created_on = models.DateField()
    updated_on = models.DateField()
    status = models.IntegerField(choices=STATUS, default=0)

    def __str__(self):
        return str(self.slug)
    




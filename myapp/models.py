from django.db import models

# Create your models here.

class User(models.Model):
    unique_id = models.AutoField(primary_key=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    age = models.CharField(max_length=2, null=False)
    sex = models.CharField(max_length=6, null=False)
    
    login_id = models.CharField(unique=True, max_length=10, blank=True, null=True)
    login_pw = models.CharField(max_length=20, blank=True, null=True)
    username = models.CharField(unique=True, max_length=8, blank=True, null=True)    

    hair_color = models.CharField(max_length=45, blank=True, null=True)
    hair_style = models.CharField(max_length=45, blank=True, null=True)
    hair_length = models.CharField(max_length=45, blank=True, null=True)
    hair_bangs = models.CharField(max_length=45, blank=True, null=True)
    eyelids = models.CharField(max_length=45, blank=True, null=True)
    glasses = models.CharField(max_length=45, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'init_user'
        

class Golajum(models.Model):
    index = models.AutoField(primary_key=True)
    login_id = models.CharField(max_length=45, blank=True, null=True)
    alc_type = models.CharField(max_length=45, blank=True, null=True)
    golm = models.TextField(blank=True, null=True)
    dscb = models.TextField(blank=True, null=True)
    
    factor = models.CharField(max_length=45, blank=True, null=True)
    scent = models.TextField(blank=True, null=True)
    alc_range_bool = models.CharField(max_length=45, blank=True, null=True)
    CE_good_bool = models.CharField(max_length=45, blank=True, null=True)
    golajum = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'golajum'
        
        
        
class Input(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
    alc_type = models.TextField()
    alc_type_dropdown = models.TextField(null=True)
    alc_ab = models.FloatField()
    alc_range = models.IntegerField(null=True)
    sweet = models.IntegerField()
    body = models.IntegerField()
    sour = models.IntegerField(null=True)
    fizzy = models.IntegerField(null=True)
    strong = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'input'


class Output(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
    alc_type = models.TextField()
    alc_ab = models.FloatField()
    alc_range = models.IntegerField(null=True)
    ml = models.IntegerField()
    price = models.IntegerField()
    CE = models.FloatField() # 용량*절대 도수 = 가성비
    CE_good = models.IntegerField() # 0.83 이상이면 1, 미만이면 0
    name_sale = models.TextField(blank=True, null=True)
    link_sale = models.TextField(blank=True, null=True)
    sweet = models.IntegerField()
    body = models.IntegerField()
    sour = models.IntegerField(null=True)
    fizzy = models.IntegerField(null=True)
    strong = models.IntegerField(null=True)
    scent = models.TextField() # list
    link_img = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = 'output'
        
        
        
class Scents(models.Model):
    scent_name = models.CharField(db_column='향의 종류', primary_key=True, max_length=10)
    scent_name_dropdown = models.TextField(db_column='분류')
    link_img = models.CharField(db_column='사진', max_length=255)
    
    class Meta:
        managed = False
        db_table = 'scent_select'
        
        
class Log(models.Model):
    index = models.AutoField(primary_key=True)
    login_id = models.CharField(max_length=45)
    date_golajum = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=45)
    alc_type = models.CharField(max_length=45)
    date_checked = models.DateTimeField(blank=True, null=True)
    date_rated = models.DateTimeField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'log'


class Location(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location'
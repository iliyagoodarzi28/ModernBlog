from django.db import models



class SiteInfo(models.Model):
    name = models.CharField(max_length=125 , verbose_name="SiteName")
    description = models.TextField(blank=True , null=True , verbose_name="SiteDescription")
    img = models.ImageField(upload_to='logo_heder/%Y/%m/%d' , blank=True , verbose_name="ImageHeader")
    phone = models.CharField(max_length=11,
     blank=True, 
     null=True, 
     default='',
     verbose_name="NumberPhone",
     help_text="0912xxxxxxxx")
    
    email = models.EmailField(max_length=255 , blank=True , null= True ,  verbose_name="Email")


    x = models.URLField(blank=True , null=True , verbose_name="X_Twitter")
    instagram = models.URLField(blank=True , null=True , verbose_name="Instagram")
    telegram = models.URLField(blank=True , null=True , verbose_name="Telegram")
    github = models.URLField(blank=True , null=True , verbose_name="GitHub")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="CreationDate")
    updated_at = models.DateTimeField(auto_now=True, verbose_name= "LastUpdatedDate" )


    class Meta:
        verbose_name = "Setting Site"
        verbose_name_plural = "Setting Site"
        ordering = ['-created_at']

    def __str__(self):
        return self.name        


    @classmethod
    def get_info(cls):
        return cls.objects.first()


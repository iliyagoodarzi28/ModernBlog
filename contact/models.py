from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=150 , verbose_name='Name')
    email = models.EmailField(verbose_name='Email')
    subject = models.CharField(max_length=200, verbose_name='Subject')
    message = models.TextField(verbose_name='Message')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='CreationDate')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Message'


    def __str__(self):
        return f"{self.name} - {self.subject}"
    

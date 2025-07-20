from django.shortcuts import render
from django.views.generic import TemplateView



class MainView(TemplateView):
    template_name = 'main/main.html'


class AboutView(TemplateView):
    template_name = 'main/about.html'

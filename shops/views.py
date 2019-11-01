from django.shortcuts import render
from django.views import generic
from django.contrib.gis.geos import fromstr,Point
from django.contrib.gis.db.models.functions import Distance
from .models import Shop
import requests
import socket
import geoip2.database
# Create your views here.
#longitude = -80.191788
#latitude = 25.761681

#user_location=Point(longitude,latitude,srid=4326)
def visitor_ip_address(request):
    x_forwarded_for=request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip=x_forwarded_for.split(',')[0]
        print("for",x_forwarded_for)
    else:
        ip=request.META.get('REMOTE_ADDR')
        print("remote",ip)
    return ip


def locate(request):

    
    #response=requests.get('http://freegeoip.net/json/')
    #geodata=response.json()
    #longitude=int(geodata['longitude'])
    #latitude=int(geodata['latitude'])
    #user_location=Point(longitude,latitude,srid=4326)
    #longitude=request.POST['longitude']
    #latitude=request.POST['latitude']
    #def post(self,request):
    template_name='shops/index.html'
    ip=visitor_ip_address(request)
    
    try:
        socket.inet_aton(ip)
        ip_valid=True
    except socket.error:
        ip_valid=False

    if ip_valid:
        reader=geoip2.database.Reader('shops/GeoLite2-City_20191029/GeoLite2-City.mmdb')
        print(ip)
        try:
            response=reader.city(ip)
            latitude=int(response.location.latitude)
            longitude=int(response.location.longitude)

        except :
            print("error occured")
            latitude=0
            longitude=0

        user_location=Point(longitude,latitude,srid=4326)
        context_object_name='shops'
        queryset=Shop.objects.annotate(distance=Distance('location',user_location)).order_by('distance')[0:6]
        reader.close()
    #if request.method =='POST':
    #    latitude=int(request.POST.get("latitude",None))
    #    longitude=int(request.POST.get("longitude",None))
        #print("success")
    #    user_location=Point(longitude,latitude,srid=4326)
        #model=Shop
        return render(request,template_name,{context_object_name:queryset})
    
    else:
        print("in_valid ip")
        return render(request,template_name,{'shops':None})
    
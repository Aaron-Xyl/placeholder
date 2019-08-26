from django.shortcuts import render
from django.shortcuts import HttpResponse
# Create your views here.

import hashlib
import os
from django import forms
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import etag
from io import BytesIO
from PIL import Image, ImageDraw
from django.core.cache import cache

class ImageForm(forms.Form):
    height = forms.IntegerField(min_value=1, max_value=2000)   #控制图片的高度和宽度
    width = forms.IntegerField(min_value=1, max_value=2000)

    def generate(self, image_format = 'PNG'):   #封装创建图片的逻辑，接受一个参数来设置图片格式，并以字节形式返回图片内容
        height = self.cleaned_data['height']
        width = self.cleaned_data['width']
        key = '{}.{}.{}'.format(width, height, image_format)  #通过宽度，高度和图片格式生成一个缓存键值
        content = cache.get(key)    #在创建新图片前，检查缓存是否储存了图片
        if content is None:
            image = Image.new('RGB',(width,height))   #由给定的宽度和高度，创建一张新图片
            draw = ImageDraw.Draw(image)                #ImageDraw会在尺寸合适的地方加入覆盖文字
            text = '{} * {}'.format(width, height)
            textwidth, textheight = draw.textsize(text)
            if textwidth<width and textheight<height:
                texttop = (height - textheight)// 2
                textleft = (width - textwidth)// 2
                draw.text((textleft, texttop), text, fill = (255, 255, 255))
            content = BytesIO
            image.save(content, image_format)
            content.seek(0)
            cache.set(key, content, 60 * 60)   #将创建的图片保存一小时
        return content

def generate_etag(requesr, width, height):
    content = 'djdb:{0} x {1}'.format(width, height)
    return hashlib.sha1(content.encode('utf-8')).hexdigest()

@etag(generate_etag)
def djdb(request,width, height):
    form = ImageForm({'height': height, 'width': width})
    if form.is_valid():
        image = form.generate()      #调用form.generate获取创建的图片
        return HttpResponse(image, content_type='image/png')
    else:
        return HttpResponseBadRequest('Invalid Image Request')

from django.urls import reverse
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

def index(request):
    example = reverse('djdb', kwargs={'width': 50 ,'height': 50})
    context = {
        'example':request.build_absolute_uri(example)
    }
    return render(request, 'home.html', context)













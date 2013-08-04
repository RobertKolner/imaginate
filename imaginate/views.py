from django.http import HttpResponse, Http404
from django.template import Context
from django.views.generic import TemplateView
from urlparse import urlparse

import errno
import os
import subprocess

class IndexView(TemplateView):
    phantomjs_path = "./imaginate/phantomjs"
    var_path = "/var/tmp/"
    
    def get(self, request, url):
        no_cache = request.GET.get("no_cache") == "1"
        image_width = request.GET.get("width") or 0
        image_height = request.GET.get("height") or 0

        image = self._get_image(url, no_cache=no_cache, width=int(image_width), height=int(image_height))

        try:
            with open(image, "rb") as f:
                return HttpResponse(f.read(), mimetype="image/jpeg")
        except IOError: 
            raise Http404

    def _get_cachedir(self):
        path = self.var_path + "imaginate/"
    
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    
        return path
    
    def _get_filename(self, url):
        if len(url) == 0:
            raise ValueError("You must provide url.")
    
        parsed = urlparse(url)
        path = parsed.netloc + parsed.path
        if path[-1] == '/':
            path = path[:-1]

        return "{}.png".format(path)
    
    def _create_image(self, url, output_path, width, height):
        script = \
    """ 
    var page = require("webpage").create();
    var url = "{url}";
    var targetWidth = {width};
    var targetHeight = {height};
    
    page.viewportSize = {{
        width: targetWidth,
        height: targetHeight
    }};

    page.open(url, function(status) {{

        var pageWidth = page.evaluate(function() {{
            return document.width;
        }});

        var zoomFactor = targetWidth / pageWidth;
        page.clipRect = {{
            top: 0,
            left: 0,
            width: targetWidth / zoomFactor,
            height: targetHeight / zoomFactor
        }}

        page.render("{output}");
        phantom.exit();
    }});
    """.format(url=url, output=output_path, width=width, height=height)
        tmp_script_path = self._get_cachedir() + 'script.js'
        tmp_script = open(tmp_script_path, 'w')
        tmp_script.write(script)
        tmp_script.close()
    
        return subprocess.check_call([self.phantomjs_path, tmp_script_path])
    
    def _get_image(self, url, width=0, height=0, no_cache=False):
        cachedir = self._get_cachedir()
        filename = self._get_filename(url)
        path = cachedir + filename
    
    
        if no_cache or not os.path.exists(path):
            self._create_image(url, path, width, height)
    
        return path


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
    
    def get(self, request):
        url = request.GET.get("url") or ""
        image_width = request.GET.get("width") or 0
        image_height = request.GET.get("height") or 0

        image_path = self._get_image(url.strip(), width=int(image_width), height=int(image_height))

        try:
            with open(image_path, "rb") as f:
                data = f.read()

            os.remove(image_path)
            return HttpResponse(data, mimetype="image/png")
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

        path = path.replace('/', '_')

        return "{}.png".format(path)
    
    def _create_image(self, url, output_path, width, height):
        script = \
    """ 
    var page = require("webpage").create();
    var url = "{url}";
   
    var defaultWidth = 1366;
    var defaultHeight = 786

    page.viewportSize = {{
        width:  {width} > 0 ? {width} : defaultWidth,
        height: {height} > 0 ? {height} : defaultHeight
    }};

    page.open(url, function(status) {{

        var offsetWidth = page.evaluate(function() {{
            return document.body.offsetWidth;
        }});

        var offsetHeight = page.evaluate(function() {{
            return document.body.offsetHeight;
        }});

        var offsetLeft = page.evaluate(function() {{
            return document.body.offsetLeft;
        }});

        var offsetTop = page.evaluate(function() {{
            return document.body.offsetTop;
        }});

        var width = page.evaluate(function() {{
            return document.width;
        }});

        var height = page.evaluate(function() {{
            return document.height;
        }});

        page.clipRect = {{
            top: offsetTop,
            left: offsetLeft,
            width: width - offsetLeft,
            height: (({height} > 0 ? {height} : offsetHeight) * (offsetWidth / ({width} > 0 ? {width} : defaultWidth))) - offsetTop
        }}

        page.render("{output}");
        phantom.exit();
    }});
    """.format(url=url, output=output_path, width=width, height=height)
        tmp_script_path = self._get_cachedir() + 'script.js'
        tmp_script = open(tmp_script_path, 'w')
        tmp_script.write(script)
        tmp_script.close()

        retval = subprocess.check_call([self.phantomjs_path, tmp_script_path])

        os.remove(tmp_script_path)
        return retval
    
    def _get_image(self, url, width=0, height=0):
        cachedir = self._get_cachedir()
        filename = self._get_filename(url)
        path = cachedir + filename
    
        self._create_image(url, path, width, height)
        
        return path


from django.http import HttpResponse, Http404
from django.template import Context
from django.views.generic import TemplateView
from urlparse import urlparse
from time import time

import errno
import os
import settings
import subprocess

def _get_os_bit_version():
    import struct
    return str(struct.calcsize("P") * 8)

class IndexView(TemplateView):
    phantomjs_path = settings.PHANTOMJS_PATH.format(bits=_get_os_bit_version())
    var_path = settings.CACHEDIR_PATH
    
    def get(self, request):
        url = request.GET.get("url") or ""
        image_width = request.GET.get("width") or 0
        image_height = request.GET.get("height") or 0

        image_path = self._get_image(''.join(url.splitlines()), width=int(image_width), height=int(image_height))

        try:
            with open(image_path, "rb") as f:
                data = f.read()

            return HttpResponse(data, mimetype="image/png")
        except IOError: 
            raise Http404

    def _get_cachedir(self):
        path = self.var_path
    
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    
        return path
    
    def _get_filename(self, url, width, height):
        if len(url) == 0:
            raise ValueError("You must provide url.")
    
        parsed = urlparse(url)
        path = parsed.netloc + parsed.path
        if path[-1] == '/':
            path = path[:-1]

        path = path.replace('/', '_')

        path += '_'+str(width)
        path += 'x'+str(height)

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
        tmp_script_path = self._get_cachedir() + 'script_{url}_{width}x{height}.js'.format(url=url[7:], width=str(width), height=str(height)).replace(":/", "_")
        tmp_script = open(tmp_script_path, 'w')
        tmp_script.write(script)
        tmp_script.close()

        retval = subprocess.check_call([self.phantomjs_path, tmp_script_path])

        try:
            os.remove(tmp_script_path)
        except IOError:
            return 1 # This has failed!
        return retval
    
    def _get_image(self, url, width=0, height=0):
        cachedir = self._get_cachedir()
        filename = self._get_filename(url, width, height)
        path = cachedir + filename
    
        if not os.path.exists(path):
            self._create_image(url, path, width, height)
        
        return path

class CacheView(TemplateView):
    var_path = settings.CACHEDIR_PATH

    def get(self, request):
        invalidate = request.GET.get("invalidate") in ("true", "True", "1")

        for (dirpath, dirnames, filenames) in os.walk(self.var_path):
            for filename in filenames:
                path = dirpath + filename
                mtime = os.path.getmtime(path)
                now = time()

                fileage = int(now - mtime)      # current file age in seconds.
                if fileage > 60 * 60 * 24 * 30:     # a month
                    try:
                        os.remove(path)
                    except IOError:
                        pass # Good.

        return HttpResponse("")

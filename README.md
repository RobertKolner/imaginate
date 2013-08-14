Imaginate
============
This little django app uses phantomjs to create screenshot of a website with given dimensions.

Usage
-------
1. Create settings.py in imaginate folder. You can just copy settings-sample.py and it will work once you supply secret key.
2. Run as a normal django-app
      
	  python ./manage.py runserver

3. Use url to make queries:

     http://127.0.0.1:8000/image/{url}

   For instance:

      http://127.0.0.1:8000/image/http://google.com

4. You can add following parameters:

     * width={int} -- Sets webview width to this value. Defaults to 1366px.
     * height={int} -- Sets webview height to this value. If the page is longer than that, it will be cropped. If it's shorter, you'll get some whitespace. Defaults to 768px, but will show whole page if not set or set to 0.

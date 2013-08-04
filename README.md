Imaginate
============
This little django app uses phantomjs to create screenshot of a website with given dimensions.

Usage
-------
1. Create settings.py in imaginate folder. You can just copy settings-sample.py and it will work once you supply secret key.
2. Run as a normal django-app
      
	  python ./manage.py runserver

3. Use url to make queries in following format:

     http://127.0.0.1:8000/image/<url>

   For example:

      http://127.0.0.1:8000/image/http://google.com

4. You can use following parameters in the url:

   * no_cache=1 -- forces the app to rebuild the image
   * width=<int> -- forces given webview size. Note that this does not guarantee that the resulting image will be this wide.
   * height=<int> -- same as above, but with height.

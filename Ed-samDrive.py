#!C:\Users\Krietallo\AppData\Local\Programs\Python\Python36-32\python.exe
import cgi, os
import cgitb;cgitb.enable()

form = cgi.FieldStorage()

# Get filename here.
fileitem = form['filename']

# Test if the file was uploaded
if fileitem.filename:
    # strip leading path from file name to avoid
    # directory traversal attacks
    fn = os.path.basename(fileitem.filename.replace("\\", "/"))
    open(fn, 'wb').write(fileitem.file.read())

    message = 'The file "' + fn + '" was uploaded successfully'

else:
    message = 'No file was uploaded'

os.rename("E:/xampp/htdocs/"+fn, "E:/course/day1/"+fn)

print ("""\
Content-Type: text/html\n
<html>
<body>
   <p>%s</p>
   <p>%s</p>
</body>
</html>
""" % (message, dir,))

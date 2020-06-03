# Django Application that works as API and runs a CRON Job

How to run : 

```
python manage.py runserver 0.0.0.0:80
```

## Admin Page
```
http://54.159.0.113/admin
username : derrick
password : derrick  
```


# Add this to the Request Headers when calling the GET Request. 
- You can find this token and create new ones from the Django Admin Dashboard. You can test it using Postman by adding the following key-value pair in Postman

```
Key : "Authorization"
Value : "Token fd314d4436dfdc9fd990822cd1e483d951c7dfd6"
```

![Postman](postman.png)

# Get Articles by Page number

```
# Example
http://54.159.0.113/articles/page/1
```

# Get Article by Searching for a <keyword>

```
# Example
http://54.159.0.113/articles/keyword/Google
```
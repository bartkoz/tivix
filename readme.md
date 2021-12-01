# Howto:
Turn on docker service, run `docker-compose up -d`
# Available endpoints:

```
/api/auth/login/
/api/auth/register/
/api/user/ POST
/api/budget/ POST/GET
/api/budget/<id>>/ GET / PATCH / PUT / DELETE
/api/budget_entries/ POST
/api/budget_entries/<id>/ POST / PATCH / PUT / DELETE
/api/category/ GET/POST
/api/category/<id>/ PATCH / PUT / GET / DELETE
```
# Filtering
Budgets can be filtered by it's categories, `icontains` logic is used to match also partially matching category names. Example: `/api/budget/?category=test`

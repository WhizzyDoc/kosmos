# kosmos
An HR Management API platform

## list of available APIs
    
### Admin
1. Main Site (SiteViewSet)
    | function | purpose | method |
    | --- | --- | --- |
    | get_site_info | To get site information | GET |
    | create_site_info | To create site info (if not exist) | POST |
    | edit_site_info | To edit site info (if created) | POST |

2. Profile (ProfileViewSet)
    | function | purpose | method |
    | --- | --- | --- |
    | create_account | To create a user account | POST |
    | register | To register the created account by filling profile details | POST |
    | authentication | To login | POST |
    | get_admin_profile | To get authenticated admin profile | POST |

3. Position (PositionViewSet)
    | function | purpose | method |
    | --- | --- | --- |
    | get_positions | To get available positions in the company | GET |

3. Department (DepartmentViewSet)
    | function | purpose | method |
    | --- | --- | --- |
    | get_departments | To get available departments in the company | GET |
### Employee

### Important Note
1. in generating dynamic URLs, check the urls.py, the url for each endpoint is generated as thus:
    * domain name (for development, **http://127.0.0.1:8000**)
    * base URL (from the project urls.py file. e.g for admin app **/api/v1/**)
    * registered class name: check the apps urls.py for the name used to register the ViewSet class name (e.g for ProfileViewSet, representing all functions under the Profile class, registered name is **profile/**)
    * function name (e.g under the ProfileViewSet, we can have **create_account/**)
    * parameters: any parameters being passed (e.g during filtering or searching, it is passed using the following syntax **?key=value**), more explanations on parameters later
    * In combination, to get an endpoint to create an account the full URL will be **http://127.0.0.1:8000/api/v1/profile/create_account/**
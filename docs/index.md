# Documentation for todo
### fastAPI: To Do API


This application has two generic endpoints:

| Method | URL Pattern           | Description             |
|--------|-----------------------|--------------------|
| GET    | /api/v1/todo/info         | Basic description of the application and container     |
| GET    | /api/v1/todo/health    | Health check endpoint     |



## CRUD Endpoints:
| Method | URL Pattern           | Description             | Example             |
|--------|-----------------------|--------------------|---------------------|
| GET    | /api/v1/todo         | List all todo     | /api/v1/todo       |
| GET    | /api/v1/todo/{id}    | Get todo by ID     | /api/v1/todo/42    |
| POST   | /api/v1/todo         | Create new todo    | /api/v1/todo       |
| PUT    | /api/v1/todo/{id}    | Update todo (full) | /api/v1/todo/42    |
| PATCH  | /api/v1/todo/{id}    | Update todo (partial) | /api/v1/todo/42 |
| DELETE | /api/v1/todo/{id}    | Delete todo        | /api/v1/todo/42    |


### Access the info endpoint
http://home.dev.com/api/v1/todo/info

### View test page
http://home.dev.com/todo/test/todo.html

### Swagger:
http://home.dev.com/api/v1/todo/docs
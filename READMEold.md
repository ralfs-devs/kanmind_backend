The project has just gotten underway and is not yet ready for use.
If you’d like to take a look, the usual disclaimer applies: 
We assume no liability for damages of any kind.

In order to install this Projekt in your local (vscode) Environment please use

git clone https://github.com/ralfs-devs/kanmind_backend
and navigate to your local project folder.

Then build a virtual environment with
python -m venv .venv # maybe you must replace 'python' to 'python3'
.venv/Scripts/activate  # for Windows users
source .venv/bin/activate  # macOS/Linux user 

then run:
pip freeze  # Which packages are already installed?
pip install -r requirements.txt  # install all necessary Packages
pip freeze  # Assure, that all Packages from requirements.txt are installed correctly

then migrate the database configuration to your local DB:
python manage.py migrate

Now you can start your local developement server with:
python manage.py runserver

For testing purposes the global rate limit ist set to "no limits".
Feel free to change the global limitation in settings.py 
by inserting your favourite rate limit values in 'DEFAULT_THROTTLE_RATES' in settings.py


Authentication APIs:
Login And Registration

API Endpoints:

    Useradministration:
    
        POST
        Path: /api/registration/
        Request Body:
        {
        "fullname": "Example Username",
        "email": "example@mail.de",
        "password": "examplePassword",
        "repeated_password": "examplePassword"
        }
        Success Response:
        {
        "token": "83bf098723b08f7b23429u0fv8274",
        "fullname": "Example Username",
        "email": "example@mail.de",
        "user_id": 123
        }

        POST
        Path: /api/login/
        Request Body
        {
        "email": "example@mail.de",
        "password": "examplePassword"
        }
        Success Response
        {
        "token": "83bf098723b08f7b23429u0fv8274",
        "fullname": "Example Username",
        "email": "example@mail.de",
        "user_id": 123
        }

    Kanmind APIs
    
    The "Boards" table represents the application's central administration
        GET 
        /api/boards/
        Description: Successful response returns a list of Boards with basic informations.
        Permissions required: User must be either owner or member of the board, he wants to visit.
        Success Response:
        [
        {
            "id": 1,
            "title": "Projekt X",
            "member_count": 2,
            "ticket_count": 5,
            "tasks_to_do_count": 2,
            "tasks_high_prio_count": 1,
            "owner_id": 12
        },
        {
            "id": 2,
            "title": "Projekt Y",
            "member_count": 12,
            "ticket_count": 43,
            "tasks_to_do_count": 12,
            "tasks_high_prio_count": 1,
            "owner_id": 3
        }
        ]
        POST
        /api/boards/
        Description: Creates a new board and adds members to it. 
        The authenticated user is as creator is automatically the owner of the board and can also add himself as member.
        Permission required: User has to be authenticated
            Request Body
            {
            "title": "Neues Projekt",
            "members": [
                12,
                5,
                54,
                2
            ]
            }
            Success Response
            The answer gives basic information for the newly created board:
            {
            "id": 18,
            "title": "neu",
            "member_count": 4,
            "ticket_count": 0,
            "tasks_to_do_count": 0,
            "tasks_high_prio_count": 0,
            "owner_id": 2
            }     


        GET
        /api/boards/{board_id}/


            Success Response
            The response returns detailed information about the board object specified in the url by board_id including member and task data.
            Permission required: Authenticated User has to be member or owner of the board to get the response.
            {
            "id": 1,
            "title": "Projekt X",
            "owner_id": 12,
            "members": [
                {
                "id": 1,
                "email": "max.mustermann@example.com",
                "fullname": "Max Mustermann"
                },
                {
                "id": 54,
                "email": "max.musterfrau@example.com",
                "fullname": "Maxi Musterfrau"
                }
            ],
            "tasks": [
                {
                "id": 5,
                "title": "API-Dokumentation schreiben",
                "description": "Die API-Dokumentation für das Backend vervollständigen",
                "status": "to-do",
                "priority": "high",
                "assignee": null,
                "reviewer": {
                    "id": 1,
                    "email": "max.mustermann@example.com",
                    "fullname": "Max Mustermann"
                },
                "due_date": "2025-02-25",
                "comments_count": 0
                },
                {
                "id": 8,
                "title": "Code-Review durchführen",
                "description": "Den neuen PR für das Feature X überprüfen",
                "status": "review",
                "priority": "medium",
                "assignee": {
                    "id": 1,
                    "email": "max.mustermann@example.com",
                    "fullname": "Max Mustermann"
                },
                "reviewer": null,
                "due_date": "2025-02-27",
                "comments_count": 0
                }
            ]
            }
            

        
        PATCH

        /api/boards/{board_id}/


        DELETE

        /api/boards/{board_id}/


        GET

        /api/email-check/

Tasks
Alles zur Bearbeitung, Erstellung und Abruf von Tasks


GET

/api/tasks/assigned-to-me/


GET

/api/tasks/reviewing/


POST

/api/tasks/


PATCH

/api/tasks/{task_id}/


DELETE

/api/tasks/{task_id}/


GET

/api/tasks/{task_id}/comments/


POST

/api/tasks/{task_id}/comments/


DELETE

/api/tasks/{task_id}/comments/{comment_id}/


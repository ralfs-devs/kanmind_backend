

# kanmind_backend

### A backend Application to provide an API for a kanban board.
#### Built with Python and Django Rest Framwork
This project is in the early testing phase.  
**Disclaimer:** We assume no liability for damages of any kind.

## Installation in Your Local VSCode Environment

1. Clone the repository:
~~~bash
git clone https://github.com/ralfs-devs/kanmind_backend
~~~

Navigate into the project folder.

Create a virtual environment:
~~~bash
python -m venv .venv
~~~
(You may need to use python3 instead of python)

Activate the virtual environment:

Windows:
~~~bash
source .venv\Scripts\activate
~~~
macOS/Linux:
~~~bash
source .venv/bin/activate
~~~
look for actually installed Dependencies:
~~~bash
pip freeze
~~~
Install required packages:
~~~bash
pip install -r requirements.txt
~~~
Check whether all the necessary dependencies are installed:
~~~bash
pip freeze
~~~
Apply database migrations:
~~~bash
python manage.py migrate
~~~
Start the development server:
~~~bash
python manage.py runserver
~~~
### Project Tree
### Testing Notes

The global rate limit is currently disabled ("no limits").
To adjust rate limiting, modify the DEFAULT_THROTTLE_RATES value in settings.py with your preferred settings.

# nipo
A classroom (or any other room) attendance tracker that uses facial recognition

This is a very new project so the Readme is currently super sketchy. However, I am trying to ensure it contains the info necessary at ths point. I am huge on documentation so be sure that as it takes shape it will be documented extensively.

## Tools to install
1. [Git](https://www.atlassian.com/git/tutorials/install-git) *Sorry I am being so obvious*
1. [Python3](https://www.python.org/downloads/)
1. [Postgresql](https://www.postgresql.org/download/)
	* Also a [Useful section on understanding roles and users in postgres](https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2#how-to-log-in-as-a-different-user-in-postgresql)
1. [Virtualenv ](https://help.dreamhost.com/hc/en-us/articles/115000695551-Installing-and-using-virtualenv-with-Python-3)(recommended)
1. sqlalchemy >Terminal/cmd command *pip install sqlalchemy*
1. Face_recognition (https://github.com/ageitgey/face_recognition) *See the module's READMe.md for installation instructions*

## After installation
After installing these tools, on your terminal:

### Clone the remote nipo repository
cd into the place where you would like your local copy of nipo to reside (you don't need to create a directory, one will be created for you) then
 ```git clone https://github.com/mcflyhalf/nipo ```  
This should copy all the contents of the nipo repository into a new folder called nipo on your system.

### Create a virtual environment to work in
At this point, on your terminal, cd into the new nipo folder that just appeared and create a new virtual environment in there using ```virtualenv .``` This assumes that Python 3 is your default version of python. If it isn't, you should instead use ```virtualenv --python=<path to python3> .```.

To activate the virtual environment, still on your terminal, you would ```source bin/activate``` and to deactivate simply type in terminal ```deactivate```. You can tell that your virtual environment is activated when the word nipo is in brackets before your usual terminal prompt.

### Install required modules
With your virtual environment activated, use ```pip install -r requirements.txt``` to install all the required python modules. Go an get some tea as this may take some time. 

### Setup db access credentials
Within the nipo root folder, check for a file called ```example_environ_vars.sh```. Make a copy of it and rename your copy to ```nipo_environ_vars.sh``` or any other name you would like. Within your copy, set the user credentials of your postgres user i.e. username, password, database (the Postgresql database that you intend to use for the nipo project) and test database (A Postgresql database that will be used for testing in the nipo project. It should necessarily be different from the main DB. Dont use the same one.) I suggest that you keep all the names I suggested and only change your username, password and port if necessary.
If you haven't already, create the Postgres user, and the 2 DB's.

The databases should be empty. Even if they arent, they will be cleared before the required tables are created. On Linux, run ```source nipo_environ_vars.sh``` (or whichever filename you chose instead) to set your environment variables to those you put in the file. 

To check that this worked, on your terminal, type ```printenv POSTGRES_USER``` the output should be the postgres username you specified on the file. To check all your other environment variables, simply use ```printenv```. There are usually quite a few of them though so finding the ones you just added may take a minute.

Ensure you do not push this particular file ```nipo_environ_vars.sh``` to github or any other remote as this is secret information and I am sure you use the password somewhere else.


### Install nipo herself
Finally, use ```pip install -e .``` within the home of the nipo project (the directory where you can see ```setup.py```). This installs the nipo module in an editable version. This will allow you to import files within nipo from other files within nipo.


### Run the test suite
There is currently no test suite. This is part of the things that need to be built into the project. Instead, we will run a small part of the project that utilises most of the existing functionality.
 cd to the nipo/tests directory. On your terminal, run ```python3 interactive_test.py```. If there are no errors, everything worked fine. If everything did indeed work fine, you should be able to go to your favourite Postgres DBRMS and check the nipo_test database and there should be some new entries. Also, in the nipo root directory there should be a file nipo.log that logged all the things that just happened.
 Finally, to run the actual test suite, then cd to ```nipo/tests``` and run ```python -m pytest```.

At this point, you may then start working on any changes you wish to work. Just select [an issue](https://github.com/mcflyhalf/nipo/issues), assign it to yourself, ask any clarifying questions on the issue itself (As comments) and then start working. When you are done, submit a pull request.



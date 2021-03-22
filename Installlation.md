# Nipo installation guide
This is a guide that walks you through the various things you need to install in order to get Nipo to work on your local machine. It is assumed that if you are able to set it up locally, you know how to do this in a production environment.
Please note that Nipo is nowhere near close to ready for use in a production environment. It is still in early stages of development.


## Tools to install
1. [Git](https://www.atlassian.com/git/tutorials/install-git)
1. [Python3](https://www.python.org/downloads/)
1. [Postgresql](https://www.postgresql.org/download/)
	* Also a [Useful section on understanding roles and users in postgres](https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2#how-to-log-in-as-a-different-user-in-postgresql). You will need this in order to setup a user with password access to Postgresql.
	* Remember the username and password that you create. This user will need createdb permission.
1. [Virtualenv ](https://help.dreamhost.com/hc/en-us/articles/115000695551-Installing-and-using-virtualenv-with-Python-3)(recommended)
1. 

## Post installation
After installing these tools, on your terminal:

### Clone the remote nipo repository
cd into the place where you would like your local copy of nipo to reside (you don't need to create a directory, one will be created for you) then
 ```git clone https://github.com/mcflyhalf/nipo ```  
This should copy all the contents of the nipo repository into a new folder called nipo on your system.

### Create a virtual environment to work in
At this point, on your terminal, cd into the new nipo folder that just appeared and create a new virtual environment in there using ```virtualenv .``` This assumes that Python 3 is your default version of python. If it isn't, you should instead use ```virtualenv --python=<path to python3> .``` (in both of these commands, not the dot (.) at the end).

To activate the virtual environment, still on your terminal, you would ```source bin/activate``` and to deactivate simply type in terminal ```deactivate``` (this is for Linux  or MacOS, for Windows, try `Scripts\activate.bat` and `deactivate` to deactivate). You can tell that your virtual environment is activated when the word nipo is in brackets before your usual terminal prompt.

### Install required modules
With your virtual environment activated, use ```pip install -r requirements.txt``` to install all the required python modules. Go and get some tea as this may take some time.

At this point, you may run into some particularly problematic modules to install which give you an error that building certain wheels failed. [A guide](https://github.com/ageitgey/face_recognition) is provided for installing the face-recognition module. The general point of the guide is that this module requires dlib which requires cmake which requires a C++ compiler. Installing these (dlib, cmake and a c++ compiler) would usually also solve errors that result when trying to install other modules such as numpy

### Setup db access credentials
Within the nipo root folder, check for a file called ```example_environ_vars.sh```. Make a copy of it and rename your copy to ```nipo_environ_vars.sh``` or any other name you would like. Within your copy, set the user credentials of your postgres user i.e. username, password, database (the Postgresql database that you intend to use for the nipo project) and test database (A Postgresql database that will be used for testing in the nipo project. It should necessarily be different from the main DB. Dont use the same one.) I suggest that you keep all the names I suggested and only change your username, password and port if necessary.
If you haven't already, create the Postgres user, and the 2 DB's on Postgresql.

The databases should be empty. Even if they arent, they will be cleared before the required tables are created. On Linux/Mac, run ```source nipo_environ_vars.sh``` (or whichever filename you chose instead) to set your environment variables to those you put in the file. On Windows, find out how to set environment variables and set them to the contents of the file (also submit a pull request to add this info to this document ;)).

To check that this worked, on your terminal, type ```printenv POSTGRES_USER``` the output should be the postgres username you specified on the file. To check all your other environment variables, simply use ```printenv``` (this is on Linux/MacOS, on Windows, find out how to show environment variables and submit PR). There are usually quite a few of them though so finding the ones you just added may take a minute.

Ensure you do not push this particular file ```nipo_environ_vars.sh``` to github or any other remote as this is secret information and I am sure you use the password somewhere else.

The project's gitignore file tries to help you not to do so.


### Install nipo herself
Finally, use ```pip install -e .``` within the home of the nipo project (the directory where you can see ```setup.py```). This installs the nipo module in an editable version. This will allow you to import files within nipo from other files within nipo.


### Run the test suite
```bash
cd nipo/tests
python3 -m pytest
```
If there are no errors, you installed everything properly. These tests are however not comprehensive and some more tests would help. If everything did indeed work fine, you should be able to go to your Postgres DBRMS and check the nipo_test database and there should be some new entries. Also, in the nipo root directory there should be a file `log/nipo.log` that logged all the things that just happened.

### Running the actual project
On your terminal, do the following:
* Go to the project's root directory (which should be called `nipo` if you simply downloaded from Github). Run the script to set environment variables (earlier referred to with suggested name `nipo_environment_vars.sh`)
* Switch to the nipo directory. At this point you should be in `path/to/project/nipo/nipo` and run `python -m flask run`. This should run the flask app. Go to the url shown on your terminal (usually 127.0.0.1:5000) and you should see Flask running
* Credentials - Credentials for all user classes are the same in the test db
	* Student - ddibala:Stud123
	* Admin - mcflyhalf:Admin123
	* Staff - starflyhalf:Staff123


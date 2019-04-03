#Preliminary Info
This is a getting started guide for new collaborators to be able to run existing functionality and understand how the whole thing works so they can then build out more functionality.

Before reading this, you should read the README to understand the purpose of this project.

#Doing basic things
This next bit is going to cover using each of the existing bits of functionality in the project.
##Marking module attendance
Run the file ```attendance.py``` found in ```nipo/```.
This file will print out some status messages to your console saying what it is doing (and you can peek into the file to see for yourself).
After running this file, check your ```nipo_test``` database and you should find that:
1. A new attendance record has been created for the module ETI001. Check this by going to your `nipo_test` db and querying the module table for the module whose ID is `ETI001`. You should find that for this module (as opposed to all the other modules or even the module before you run the file) has an attendance record. The actual value of the attendance record is gibberish because it is a serialised/pickled list. If you copy it then unpickle it you may get the actual value but you dont quite need to do this.
1. The attendance record for the session created above been updated with a new class session (You wont be able to see this unless you can unpickle the raw value from the db which I advise you not to worry about at the moment)
1. Some students have been marke as having attended this class session. (Again you can only actually see this if you unpickle the data)

Now, run this file again but this time in a REPL. You can do this using `python -i attendance.py`. Then try to:
0. Use `mod.getAttendance()` to see the unpickled attendance record.
0. See whether you are able to use mod.updateAttendance to mark the student whose name is `Chumo Chacha` present for this module.

If you can do this then you are ready to work on other attendance related aspects of the project. Before you do however, run the test suit again `python -m pytest` to make sure you havent broken anything in the process.
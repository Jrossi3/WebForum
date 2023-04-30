# Name + Stevens Login
Jason Rossi, jrossi3@stevens.edu
Nouman Syed, nsyed1@stevens.edu

# The URL of your public GitHub repo
https://github.com/Jrossi3/WebForum

# an estimate of how many hours you spent on the project
Each of the group members spent around 20 hours on the project

# a description of how you tested your code
The way we tested our code was through a test.sh file. In this file, we would run shell commands to test each of the routes we had put together. 

# any bugs or issues you could not resolve
There were no bugs or issues that we could not resolve.

# an example of a difficult issue or bug and how you resolved
An example of a difficult issue or bug was extracting a key from the shell command and putting it into another shell command. 

# a list of the five extensions you’ve chosen to implement; be sure to describe the endpoints you’ve added to support this, using a documentation format similar to ours
1) Update function
This is the route used for the update feature: @app.route("/post/<int:id>/update/<string:key>", methods=["PUT"])

2) Fulltext search
This is the route used for the fulltext search feature: @app.route("/post/fulltext/<string:msg>", methods=['GET'])

3) Persistence
No endpoints, used a mongo database to keep track of everything. 

# detailed summaries of your tests for each of your extensions, i.e., how to interpret your testing framework and the tests you’ve written

1) Update Post

We tested the update message post feature in a very straightforward way. We ran the command "curl http://127.0.0.1:5000/post -X POST -d '{"msg": "hi my name is jason"}'" to add a new post. After this, we set RESPONSE equal to the new post. We then got the key, msg, and id of the new post and ran the update command: "curl -X PUT -d '{"msg": "hello I am update"}' http://127.0.0.1:5000/post/$id/update/$key". This changed the message from "hi my name is jason" to "hello I am update". We then got the updated post and set it equal to New. Then we got the updated message and set it equal to newMsg. From here, we checked if msg and newMsg were equivalent to each other. If they were equal, then the update function has failed to update the message. If they are not equal, then the message was updated. 

2) Fulltext Search

We tested persistence in a very simple way. We ran the command "curl http://127.0.0.1:5000/post -X POST -d '{"msg": "hi my name is jason"}'" to add a new post. We then ran the command 'curl http://127.0.0.1:5000/post/fulltext/"hi%20my%20name%20is%20jason"' to find all matching posts with the message "hi my name is jason" essentially targeting the post we just created. This command was set equal to "RESPONSE". We then created an EXPECTED variable, which was then set to the new post that was just created, but the way it was put together was by extracting the information from the new post that was just created and then adding it to a EXPECTED variable. Then we checked if the EXPECTED was equivalent to the RESPONSE and if they were, then the test passed since the search found the new post with the matching message.

3) Persistence

We tested persistence through 2 different ways. Our first way was restarting the server through running two commands to end and start the server. There is a "kill $PID" command and a "flask run &" command to end and start the server resepctively. The second way of testing was giving it a bad request. The exact command is "curl http://127.0.0.1:5000/post/fulltext" and here this is a bad request because it is an unfinished request and therefore will return an error. Then there is a test to see if the post is still existing after the command is run. There are many comments in the testing to show the exact specifics of when these tests occur. 

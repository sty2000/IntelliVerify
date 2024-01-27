# IntelliVerify
 Implement a program that improve the performance of large language models (LAMMA). To this end, your solution is asked to 1) parse the output of a language model and to extract a clean answer and 2) check, with the aid of existing knowledge bases, which are available on the web, whether the answer is correct or not

## Setup
1. Transmit the source code to the docker image
 Use the command "docker cp /IntelliBerify $(ImageID):/app/"

2. Install the requirements.
Go into the terminal of the docker, then "$cd ~/IntelliVerify/".
 Install pipreqs(if haven't), command "$pip install pipreqs",
 Then "$pipreqs . --encoding=utf-8"
 Then "$pip install -r requirements.txt"
 After these, the requirements are done.

3. Download the required pre-trained models.
   From here (PUT YOUR GOOGLE DRIVE LINK HERE) you can download the "model_squad.pt" file which is used for answer extraction module.
   Then trasmit it into the folder of IntelliVerify, command: "docker cp /model_squad.pt $(ImageID):~/IntelliBerify".
   
4. Execute main.py to see the results.
 Open the docker's terminal, then "$cd ~/IntelliVerify/"
 Then execute by "$python3 main.py"
 The result of each input will be printed in the terminal.
 Besides, after the program is done, all the information will be written into the "example_output.txt" file.

5. If you want to change a test set, .....
 Just replace the "example_input.txt" file to the one you hope to use for test. The format should be consist with the original example_input file (we follows the format of assignment).

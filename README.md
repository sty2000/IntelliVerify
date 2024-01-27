# IntelliVerify Introduction
This is a pratical assignment for the course Web Data Processing Systems named IntelliVerify.

This program is designed to improve the performance of large language models such as LLaMA. Our main implementations include: 

1) Given certain types of questions, parse the output of LLaMA and extract a clean answer;

2) With the aid of Wikipedia, link the answer to an entity and decide the answer's correctness.

## Setup
To run this program locally, please follow the next procedure:

1. Use the Docker image loaded with 7B parameters llama2 model (provided).

- To download the docker image, type command: `docker pull karmaresearch/wdps2`
- To run the docker image, type command: `docker run -ti karmaresearch/wdps2`
2. Transmit the source code to the docker image.
- Enter the IntelliVerify file

- Use the command `docker cp ./IntelliVerify $(ContainerID):/home/user/`

  > Please remember to change the ContainerID to your local container ID with the help of `docker ps -a`.

3. Install the requirements.

  - Go into the terminal of the docker, then `$cd ~/IntelliVerify/`.
  - Install pipreqs via command `$pip install pipreqs`, then `$pipreqs . --encoding=utf-8`.
  - Then `$pip install -r requirements.txt`.

4. Download the pre-trained model for answer extracting.
  - From [here](https://drive.google.com/file/d/1Az-K97XyECQ7Drvf_6MdCOVxBv9Shi2B/view?usp=drive_link) you can download the "model_squad.pt" file which is used for the answer extraction module.
  - copy it into the folder of IntelliVerify: `docker cp /model_squad.pt $(ContainerID):~/IntelliVerify`.

5. Execute the program to see the results.

- Type in your questions to `input_example.txt`. If you do not have specific questions to ask, you can also just use the default questions in this file. 
- Open the docker's terminal, then `$cd ~/IntelliVerify`,then execute `$python3 main.py`.
 - After the program is executed, the result of each input will be printed in the terminal. The answers will be written into the `example_output.txt` file.

## Program Structure
---- IntelliVerify\  
&emsp;|---- README.md  
&emsp;|---- Similarity.py  
&emsp;|---- WikiReq.py   
&emsp;|---- access_llm.py    
&emsp;|---- example_input.txt  
&emsp;|---- extract_answer.py  
&emsp;|---- main.py  
&emsp;|---- ner.py  
&emsp;|---- output.txt  
&emsp;|---- requirements.txt  

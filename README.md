# IntelliVerify
This is a pratical assignment for the course Web Data Processing Systems.

This program is designed to improve the performance of large language models such as LLaMA. Our main implementations include: 

1) Given certain types of questions, parse the output of LLaMA and extract a clean answer;

2) With the aid of Wikipedia, link the answer to an entity and decide the answer's correctness.

## Setup
To run this program locally, please follow the next procedure:

0. Download the initial docker image:
- `docker pull karmaresearch/wdps2`

2. Transmit the source code to the docker image.
- Use the command `docker cp /IntelliVerify $(ImageID):/app/`

2. Install the requirements.
  - Go into the terminal of the docker, then `$cd ~/IntelliVerify/`.
  - Install pipreqs via command `$pip install pipreqs`, then `$pipreqs . --encoding=utf-8`.
  - Then `$pip install -r requirements.txt`.


3. Download the pre-trained model for answer extracting.
   From [here](https://drive.google.com/file/d/1Az-K97XyECQ7Drvf_6MdCOVxBv9Shi2B/view?usp=drive_link) you can download the "model_squad.pt" file which is used for the answer extraction module.
   Then, copy it into the folder of IntelliVerify: `docker cp /model_squad.pt $(ImageID):~/IntelliVerify`.
   
4. Execute the program to see the results.
- Open the docker's terminal, then `$cd ~/IntelliVerify/`,
 then execute `$python3 main.py`.
- Type in your questions to `input_example.txt`. If you do not have specific questions to ask, you can also just use the default questions in this file.
 - After the program is executed, the result of each input will be printed in the terminal. The answers will be written into the `example_output.txt` file.




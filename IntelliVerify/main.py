from access_llm import llm_answer
from extract_answer import answer_extract
from ner import entities_extract
import Similarity as fc

FILE_PATH = "./input_example.txt"


def process_input(file_path):
    """
    Input document path, output (id,question) list
    :param file_path:
    :return: questions_list
    """
    questions_list = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # content = file.readlines()
            # lines = content.split('\n')
            lines = file.readlines()
            print(lines)
            for line in lines:
                if line == [] or line == ['\n']:
                    continue
                questions = line.strip().split('\t')
                if questions[1][0:8] == "Question":
                    questions[1] = questions[1][8:-7]

                print(questions)
                question_id = questions[0][-3:]
                print(question_id)
                questions_list.append((question_id, questions[1]))
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return questions_list



def intelli_verify(questions_list):
    """
    &lt;ID question&gt;&lt;TAB&gt;[R,A,C,E]&lt;answer&gt; where
    "R" indicates the raw text produced by the language model,
    "A" is the extracted answer,
    "C" is the tag correct/incorrect
    "E" are the entities extracted.
    :param questions_list:
    :return:
    """
    output_file = open('output.txt', 'w')
    for (question_id, question) in questions_list:
        R = llm_answer(question)  # 大语言模型生成的答案
        A = answer_extract(question, R)  # 答案抽取，一个实体或yes/np
        C = fc.fact_check(question=question, ans_llm=A)  # 喜同部分，返回"correct"或"incorrect"
        E1 = entities_extract(question)  # 天宜部分，返回的是一个list，list中元素为元组(entity，wiki_link)
        E2 = entities_extract(R)
        E = list(set(E1 + E2))  # 去重
        if classify_question(question):  # 如果是特殊疑问句
            for entity_pair in E:
                entity_name = entity_pair[0].lower()
                if entity_name.find(A.lower()) != -1 or A.lower().find(entity_name) != -1:
                    A = entity_pair[1]
        #E = [("paris","https://en.wikipedia.org/wiki/Paris")]
        result = ""
        begin = "question-" + question_id + "\t"
        result = result + begin + "R" + '"' + R + '"\n'
        result = result + begin + "A" + '"' + A + '"\n'
        result = result + begin + "C" + '"' + C + '"\n'
        for entity_pair in E:
            result = result + begin + "E" + '"' + entity_pair[1] + '"\n'
        #print(result)

        output_file.write(result)
    output_file.close()

questions_list = process_input(FILE_PATH)
intelli_verify(questions_list)



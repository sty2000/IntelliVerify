import WikiReq
import spacy
from nltk import FreqDist
from nltk.tokenize import word_tokenize
import numpy as np

special_set = set(("What", "Where", "When", "Who", "Why", "Which", "Whose", "How"))
key_ans = "Shenzhen"
key_question = ["China","province"]
map_dictionary = {}
text_vec = []
key_vec = []

# print(text)
nlp = spacy.load("en_core_web_sm")
import en_core_web_sm

def get_text() -> list:
    text = WikiReq.get_wikipedia_content(key_ans)
    for i in range(len(key_question)):
        text += " " + WikiReq.get_wikipedia_content(key_question[i])
    return text

def get_keywords(nlp,text:str) -> list[str]:
    nlp = en_core_web_sm.load()
    doc = nlp(text)
    keywords = [token.text for token in doc if not token.is_stop and token.is_alpha]
    keywords = [word.lower() for word in keywords]
    return keywords

def vectorize_text(text:list[str]) -> list[int]:
    global map_dictionary
    map_dictionary = {word: idx for idx, word in enumerate(set(text))}
    mapping_func = np.vectorize(lambda x: map_dictionary[x])
    text_vector = mapping_func(text)
    keyword_lst = []
    keyword_lst.append(map_dictionary.get(key_ans.lower(), -1))
    for i in range(len(key_question)):
        keyword_lst.append(map_dictionary.get(key_question[i].lower(), -1))
    return text_vector, keyword_lst

def decay_exponential(dist:int) -> float:
    base = 2
    score = base ** float(1-dist)
    return score

def decay_power(dist:int) -> float:
    coef = 1
    score = coef * (1 / dist)
    return score

def get_score() -> float:
    pos_lst = []
    for i in range(len(key_vec)):
        pos_lst.append(np.where(text_vec == key_vec[i])[0])
        # print(np.where(text_vec == key_vec[i])[0])

    # print(f'Checking the score of {key_ans}:')
    # print(pos_lst)
    # print(len(pos_lst))
    # pos_list: row0 for keyword of answer(BEIJING), row1 & 2 for keywords of question (CHINA, CAPITAL)
    sum = 0
    for i in range(len(pos_lst[0])):
        for j in range(len(pos_lst[1])):
            for k in range(len(pos_lst[2])):
                dist1 = abs(pos_lst[0][i] - pos_lst[1][j])
                dist2 = abs(pos_lst[0][i] - pos_lst[2][k])
                sum += decay_exponential((dist1 + dist2) / 2)
            # sum += decay_power(abs(pos_lst[0][j] - pos_lst[i][k]))
            # pass
    # print(f'score for {key_ans} is {sum}')
    return sum

def get_question(question:str, answer:str) -> None:
    global key_question, key_ans
    Q = get_keywords(nlp, question)    
    if question.split()[0] in special_set: # special
        # print("special question")
        key_question[0] = Q[0]
        key_question[1] = Q[1]
        key_ans = answer
        # Q
    else: # general
        # print('normal question')    
        key_ans = Q[0]
        key_question[0] = Q[1]
        key_question[1] = Q[2]
        # print(Q)
    # print(Q)
    return None

def fact_check(question:str, ans_llm:str) -> str:
    global text_vec, key_vec
    try:
        get_question(question, ans_llm)
        # return
        text = get_text()
        text = get_keywords(nlp,text)
        # print(text) # see what get from wiki
        text_vec, key_vec = vectorize_text(text) # key_vec: [ans, ques[0], ques[1], ... ques[n]]
        score = get_score()
        if score > 0.1:
            if ans_llm == "no":
                return "Incorrect"
            return "Correct"
        else:
            return "Incorrect"
    except:
        return "True"




# print(fact_check(question="is Beijing the capital of China?", ans_llm="Beijing"))
# exit()

# print(get_keywords(nlp, question))


# print(text_vec)
# np.where(text_vec == key_vec[0])[0]
# np.where(text_vec == key_vec[1])[0]
# print(np.where(text_vec == key_vec[2])[0])


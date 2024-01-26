import spacy
import os
from nltk.tokenize import word_tokenize
import wikipediaapi
import os
import re
import concurrent.futures
from collections import defaultdict

SAVE_FILE_PATH = "./wiki_repo/"


def crawl_and_save(title):
    page = wiki_wiki.page(title)
    #print(title)

    # 构建文件路径
    file_path = os.path.join(folder_path, f'{title}.txt')

    truncated_title = title[1:100]
    # 将标题和摘要保存到单独的文件中
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"Title: {truncated_title}\n")
        file.write(f"Summary: {page.summary}\n")
        file.write("------\n")

def calculate_jaccard_similarity(input_sentence, text_file_path):
    with open(text_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    input_tokens = set(word_tokenize(input_sentence.lower()))
    text_tokens_sets = [set(word_tokenize(line.lower())) for line in lines]

    similarities = [len(input_tokens.intersection(text_tokens)) / len(input_tokens.union(text_tokens)) for text_tokens in text_tokens_sets]

    max_similarity_index = similarities.index(max(similarities))
    max_similarity_score = max(similarities)

    return max_similarity_score

def find_most_similar_file(input_sentence, corpus_dir):
    most_similar_score = -1
    most_similar_file = None

    for filename in os.listdir(corpus_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(corpus_dir, filename)
            similarity_score = calculate_jaccard_similarity(input_sentence, file_path)

            if similarity_score > most_similar_score:
                most_similar_score = similarity_score
                most_similar_file = filename

    return most_similar_file, most_similar_score

def entities_extract(text):
    global wiki_wiki, folder_path
    wiki_wiki = wikipediaapi.Wikipedia('english')
    nlp = spacy.load("en_core_web_sm")
    # 处理文本，获取 spaCy 的文档对象
    doc = nlp(text)

    ent_list = []
    #打印每个单词和其对应的实体标签
    for ent in doc.ents:
        #print(text)
        ent_list.append(ent.text)
        #print(f"{ent.text}: {ent.label_}")

    #print(ent_list)

    wsd = []
    for ent in ent_list:
        page_py = wiki_wiki.page(f'{ent}_(disambiguation)')
        text = page_py.text

        pattern = re.compile(r'\n([^\n,]+),')
        matches = pattern.findall(text)
        matches = [match.replace('"', '') for match in matches]

        #print(matches)

        modified_list = [f"https://en.wikipedia.org/wiki/{item}" for item in matches]

        save_dir = r'SAVE_FILE_PATH'
        os.makedirs(save_dir, exist_ok=True)

        folder_path = os.path.join(SAVE_FILE_PATH, ent)
        os.makedirs(folder_path, exist_ok=True)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 在线程池中提交任务
            executor.map(crawl_and_save, matches)

        # 使用 ThreadPoolExecutor 创建线程池
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 在线程池中提交任务
            executor.map(crawl_and_save, matches)

        sub_string = text.replace(ent, '')
        most_similar_file, similarity_score = find_most_similar_file(sub_string, folder_path)
        # print("实体：", ent)
        # print("最相似的文本文件：", most_similar_file)
        # print("相似度得分：", similarity_score)
        if most_similar_file is not None:
            ent_name = most_similar_file.split('.')[0]
            #print("!!", ent_name)
            wsd.append(ent_name)
    result_tuples = [(item, f'https://en.wikipedia.org/wiki/{item}') for item in wsd]

    return result_tuples


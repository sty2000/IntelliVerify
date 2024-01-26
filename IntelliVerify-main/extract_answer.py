import re
import torch
import re
import nltk
import string
import collections
from torch import softmax
from transformers import BertTokenizerFast, BertForQuestionAnswering
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_path = "./model_squad.pt"
BERT_MODEL_NAME = 'bert-base-uncased'
GENERAL_QUESTION = 0
SPECIAL_QUESTION = 1
PREDICTED_NO = 0
PREDICTED_YES = 1
PREDICTED_OTHER = 2

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


def classify_question(question):
    """
    Determine whether the question is a general or special question based on
    the first word of the question.
    :param question:
    :return:
    """
    # Remove Punctuation from a Sentence
    question = question.lower()
    question = re.sub(r'[^\w\s]', '', question)
    general_question_sentences = ["yes or no", "is it true", "is it correct", "do you agree"]
    # Get sentence starters and ending punctuation marks
    start_word = question.split()[0]
    end_punctuation = question[-1] if question[-1] in ['.', '?', '!'] else ''
    # general question keywords
    general_question_words = ['is', 'are', 'am', 'was', 'were', 'do', 'does', 'did',
                              'have', 'has', 'had', 'can', 'could', 'will', 'shall', 'may',
                              'might', 'should', 'would']
    for general_question_sentence in general_question_sentences:
        if general_question_sentence in question:
            return GENERAL_QUESTION
    if start_word in general_question_words:
        return GENERAL_QUESTION
    else:
        return SPECIAL_QUESTION


def process_special_question(query, context):
    """

    :param query:
    :param context:
    :return:
    """
    tokenizer = BertTokenizerFast.from_pretrained(BERT_MODEL_NAME)
    model = BertForQuestionAnswering.from_pretrained(BERT_MODEL_NAME).to(device)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')), strict=False)
    with torch.no_grad():
        model.eval()
        inputs = tokenizer.encode_plus(text=context, text_pair=query, max_length=512, padding='max_length',
                                       truncation=True, return_tensors='pt').to(device)
        outputs = model(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'],
                        token_type_ids=inputs['token_type_ids'])
        ans_start = torch.argmax(outputs[0])
        ans_end = torch.argmax(outputs[1])
        ans = tokenizer.convert_tokens_to_string(
            tokenizer.convert_ids_to_tokens(inputs['input_ids'][0][ans_start:ans_end + 1]))
        return ans


def process_general_question(context):
    """
    The fine-toned bert model is used to determine whether an answer expresses yes or no.
    The answer is divided into sentences before input,
    and each sentence is fed into the model separately to obtain a prediction,
    with the final result based on a comparison of the number of yes and no sentences.
    :param context:
    :return:
    """
    num_yes = 0
    num_no = 0
    tokenizer = AutoTokenizer.from_pretrained("sachin19566/distilbert_Yes_No_Other_Intent")
    model = AutoModelForSequenceClassification.from_pretrained("sachin19566/distilbert_Yes_No_Other_Intent")
    # Converting text to model input format using tokenizer
    sentences = nltk.sent_tokenize(context)
    for sentence in sentences:
        if_yes = 0
        words = sentence.split()
        #words = [word for word in words if all(char not in string.punctuation for char in word)]
        # words = nltk.word_tokenize(sentence)
        # print("original words:",words)
        # #Remove punctuation
        # # Define regular expressions that match all punctuation but single quotes and Hyphen
        # punctuation_pattern = re.compile(r"[^\w'-]")
        # # Filter Punctuation
        # words = [punctuation_pattern.sub('', word) for word in words]
        # # Remove empty strings
        # words = list(filter(None, words))
        # print("processed words,",words)
        for word in words:
            inputs = tokenizer(word, return_tensors="pt")
            # Inferences using models
            with torch.no_grad():
                outputs = model(**inputs)
            # Getting the model's predictions
            logits = outputs.logits
            probabilities = softmax(logits, dim=1)
            # predicted results
            predicted_class = torch.argmax(probabilities, dim=1).item()
            probabilities = probabilities.tolist()[0]
            # print(word,"predicted_class = ",predicted_class,"probabilities=",probabilities)
            if predicted_class == PREDICTED_YES: if_yes += probabilities[PREDICTED_YES]
            if predicted_class == PREDICTED_NO: if_yes -= probabilities[PREDICTED_NO] * 5 #  权重控制
            # print("if_yes=",if_yes)
        if if_yes >= 0: num_yes += 1
        else: num_no += 1
        # print("sentence:",sentence)
        # print("num_yes = ",num_yes,"   num_no=",num_no)

    if num_yes > num_no:
        return PREDICTED_YES
    else:
        return PREDICTED_NO


# print("the sky is blue.")
# print(process_general_question("the sky is blue."))
# print("the sky is not blue.")
# print(process_general_question("the sky is not blue."))
# print("the sky is hardly blue.")
# print(process_general_question("the sky is hardly blue."))
# print("the sky can't be blue.")
# print(process_general_question("the sky can't be blue."))

# answers = [
#     "Yes, the sky appears blue during the day due to the scattering of sunlight by the Earth's atmosphere. This phenomenon, known as Rayleigh scattering, causes shorter wavelengths of light, such as blue and violet, to scatter more.",
#     "Absolutely. Sunlight is crucial for photosynthesis, a process in which plants convert light energy into chemical energy to produce their own food. Lack of sunlight can hinder this process and negatively impact plant growth.",
#     "humans cannot naturally breathe underwater. Unlike fish, our respiratory system is adapted to extract oxygen from the air. Breathing underwater without specialized equipment would lead to drowning.",
#     "No, the Earth is not flat; it is an oblate spheroid. This has been confirmed through various scientific observations, including satellite imagery, gravity measurements, and circumnavigation.",
#     "Yes, birds do have bones. In fact, birds have a lightweight skeletal structure adapted for flight. Their bones are hollow and contain air sacs, contributing to their overall buoyancy.",
#     "Contrary to popular belief, it is challenging to see the Great Wall of China with the naked eye from space. The wall is relatively narrow, and its color blends with the natural surroundings.",
#     "While both diamonds and coal are forms of carbon, diamonds are not made from compressed coal. Diamonds form deep within the Earth's mantle under high pressure and temperature conditions.",
#     "No, lightning is not hotter than the sun. Lightning can reach temperatures of around 30,000 Kelvin, while the sun's core temperature is about 15 million Kelvin.",
#     "It is possible to sneeze with your eyes open, but it is a natural reflex for most people to close their eyes during a sneeze. The myth that your eyes will pop out if you sneeze with them open is not true.",
#     "Not necessarily. The boiling point of water depends on atmospheric pressure. At higher altitudes, where atmospheric pressure is lower, water boils at temperatures below 100 degrees Celsius."
# ]
# results = []
# for i in range(0, 10):
#     results.append(process_general_question(answers[i]))
#     print(results[i])
#     print('\n')

def answer_extract(query, context):
    if classify_question(query) == SPECIAL_QUESTION:
        answer = process_special_question(query, context)
        return answer

    else:
        ans = process_general_question(context)
        if ans == PREDICTED_YES:
            return "yes"
        else:
            return "no"


questions = [
    "What is the capital city of France?",
    "How many continents are there on Earth?",
    "Who wrote the play 'Romeo and Juliet'?",
    "What is the currency of Japan?",
    "What is the largest mammal in the world?",
    "In what year did the Titanic sink?",
    "What is the chemical symbol for gold?",
    "Who painted the Mona Lisa?",
    "What is the capital city of Australia?",
    "In what year did the United States declare its independence?",
    "Is the Great Wall of China visible from space?",
    "Are penguins found in the Arctic?",
    "Can humans breathe underwater using scuba gear?",
    "Is English the most widely spoken language in the world?",
    "Do all continents have deserts?"
]
answers = [
    "The capital city of France is Paris. Renowned for its iconic landmarks such as the Eiffel Tower and the Louvre Museum, Paris is a global center for art, fashion, and culture. It is situated on the Seine River and is known for its rich history, exquisite cuisine, and charming architecture.",

    "There are seven continents on Earth. These continents are Asia, Africa, North America, South America, Antarctica, Europe, and Australia. Continents are large landmasses that are defined by their unique geological and geographical features, and they play a crucial role in shaping the planet's ecosystems.",

    "William Shakespeare wrote the play 'Romeo and Juliet.' As one of his most famous works, the play is a tragic love story between the titular characters from feuding families. Shakespeare's eloquent use of language and exploration of human emotions make 'Romeo and Juliet' a timeless classic in literature.",

    "The currency of Japan is the Japanese Yen. Derived from the Latin word 'aurum,' gold is a precious metal known for its lustrous yellow color and has been valued for its rarity and beauty throughout human history. It is often used in jewelry, coinage, and various industrial applications.",

    "The blue whale is the largest mammal in the world. These magnificent marine mammals can reach lengths of up to 100 feet and weigh as much as 200 tons. Blue whales are known for their distinct blue-gray coloration and are found in oceans across the globe, primarily feeding on small shrimp-like animals called krill.",

    "The Titanic sank in the year 1912. The tragic sinking of the RMS Titanic occurred on its maiden voyage from Southampton to New York City. The ship, considered unsinkable, hit an iceberg in the North Atlantic, leading to the loss of more than 1,500 lives and becoming one of the most infamous maritime disasters in history.",

    "The chemical symbol for gold is Au. Derived from the Latin word 'aurum,' gold is a precious metal known for its lustrous yellow color and has been valued for its rarity and beauty throughout human history. It is often used in jewelry, coinage, and various industrial applications.",

    "Leonardo da Vinci painted the Mona Lisa. Created between 1503 and 1506, this masterpiece is renowned for the subject's enigmatic smile and Leonardo's unparalleled skill in capturing subtle expressions. The painting is housed in the Louvre Museum in Paris and is considered one of the most iconic works of art.",

    "The capital city of Australia is Canberra. Established in 1908 as the capital to resolve the rivalry between Sydney and Melbourne, Canberra is located in the Australian Capital Territory. It serves as the seat of the Australian government and is known for its well-planned layout and significant national institutions.",

    "The United States declared its independence in the year 1776. The Declaration of Independence, drafted primarily by Thomas Jefferson, was adopted by the Continental Congress on July 4, 1776. This historic document proclaimed the thirteen American colonies as independent states, paving the way for the formation of the United States of America."

    "The Great Wall of China is generally not visible from space with the naked eye. Despite being long, it is narrow, and the color blends with the natural surroundings, making it challenging to spot from space without aid.",

    "No, penguins are not found in the Arctic. Penguins are native to the Southern Hemisphere, primarily in Antarctica, South America, Africa, Australia, and New Zealand.",

    "With the use of scuba gear, humans can breathe underwater for limited periods. Scuba divers carry compressed air tanks and a regulator to breathe while exploring underwater environments.",

    "English is not the most widely spoken language by the number of native speakers. Mandarin Chinese holds that distinction. However, English is widely used as a global lingua franca and is one of the most commonly spoken languages overall.",

    "No, not all continents have deserts. While Africa is home to the largest hot desert, the Sahara, and Antarctica is the largest cold desert, other continents, such as Europe, have minimal desert areas or none at all."
]

# for i in range(0,15):
#     print("******************************************************************************")
#     print("question:",questions[i],"\nanswer:",answers[i],"\n")
#     print("extract answer:",answer_extract(questions[i],answers[i]))



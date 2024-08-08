import os 
import streamlit as st 
from langchain_openai import ChatOpenAI
from langchain.prompts import  PromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser 

model_name = st.secrets["AI_MODEL"]
api_key = st.secrets["AI_API_KEY"]
 
st.header("Thai Quiz")
json_parser = SimpleJsonOutputParser()
 
if 'selected_categories' not in st.session_state:
    st.session_state.selected_categories = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "questions" not in st.session_state:
    st.session_state.questions = []

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

if "feedback" not in st.session_state:
    st.session_state.feedback = []

if "answer" not in st.session_state:
    st.session_state.answer = []

def get_model():
    return ChatOpenAI(base_url='https://api.opentyphoon.ai/v1',
                    model=model_name,
                    api_key=api_key,
                    temperature=0.5,)


model = get_model()
 

def choose_topic():
    categories = ",".join(st.session_state.selected_categories)
    prompt = get_generation_question_prompt()
    st.session_state.chat_history.append(prompt.format(category=categories))
    st.session_state.questions = (prompt | model | json_parser).invoke(categories)
    st.session_state.clicked = True
    
def get_student_answer_for_question():
    answers = []
    for i, q in enumerate(st.session_state.questions):
        answer = """question={question} choices={choices} answer={answer}""".format(question=st.session_state.questions[i]["question"], answer=st.session_state[f"radio_{i}"], choices=",".join(st.session_state.questions[i]["options"]))
        answers.append(answer)

    return answers

def submit():
    student_answers = " ".join(get_student_answer_for_question())    
    prompt = get_submit_question_prompt()
    st.session_state.chat_history.append(prompt.format(student_answers=student_answers))
    st.session_state.feedback = (prompt | model | json_parser).invoke(student_answers)
    st.session_state.clicked = True
    

def select(question_index):
    st.session_state[f"question_{question_index}"] = st.session_state[f"radio_{question_index}"]

def reset():
    st.session_state.clicked = False
    st.session_state.selected_categories = []

    st.session_state.chat_history = []
    st.session_state.feedback = []
    st.session_state.answer = []
    print(range(len(st.session_state.questions)))
    for i in range(len(st.session_state.questions)):
        del st.session_state[f"question_{i}"]
        del st.session_state[f"radio_{i}"] 
    st.session_state.questions = [] 
    

def get_generation_question_prompt() -> str:
    prompt = PromptTemplate(
        input_variables=["category"],
        # template="""
        #     You are a Thai teacher who is good at creating Thai quizzes.
        #     You are creating a Thai quiz for your students.
        #     The question language is in English.
        #     But the options language is in Thai.
        #     The question should not be ambiguous.            
        #     It has 3 levels of difficulty: easy, medium, and hard.
        #     Each level has 1 questions except for the easy level which has 1 questions.
        #     Each question has 4 options.
        #     The correct answer is in Thai and be the value of the correct option not the index. 
        #     The category of this quiz is {category}.
        #     each question should have array of json format like this:
        #     "id": 1, "question": "What is the capital of Thailand?", "options": ["กรุงเทพ", "ฮานอย", "มานิลา", "จาการ์ต้า"], "answer": "กรุงเทพ".
        #     it should only output a list of questions, and no another text.
        #     after students submit their answers, you should provide array of feedback for all question each feedback should have the same format as the question except it has an additional field called "student_answer" and "feedback" e.g. "id": 1, "question": "What is the capital of Thailand?", "options": ["กรุงเทพ", "ฮานอย", "มานิลา", "จาการ์ต้า"], "answer": "กรุงเทพ", "student_answer": "ฮานอย", "feedback": "The correct answer is กรุงเทพ.". 
        #     after providing feedback, you should create a new question based on the previous submissions from the students.
        #     if the student answer is correct, you should create a new question that is similar to the previous question.
        #     if the student answer is wrong, you should create a new question that is different from the previous question.
        #     the new question should have the same format as the previous question.
        #     you should keep track of the student's progress and provide feedback based on their performance.
        #     if the student is doing well, you should provide more challenging questions.
        #     if the student is struggling, you should provide easier questions.
        # """)
        template="""
            You are a Thai teacher skilled in creating quizzes. The category of this quiz is {category}. Create a Thai quiz with questions in English and options in Thai. Include three levels of difficulty: easy, medium, and hard. The easy level has one question, while medium and hard levels each have one question. Each question should have four options in Thai, and the correct answer should be provided in Thai, not as an index. Format each question as a JSON object with fields like id, question, options, and answer. For example, the question might look like: "id": 1, "question": "What is the capital of Thailand?", "options": ["กรุงเทพ", "ฮานอย", "มานิลา", "จาการ์ต้า"], "answer": "กรุงเทพ".
            After students submit their answers, provide feedback in the following format: "id": 1, "question": "What is the capital of Thailand?", "options": ["กรุงเทพ", "ฮานอย", "มานิลา", "จาการ์ต้า"], "answer": "กรุงเทพ", "student_answer": "ฮานอย", "feedback": "The correct answer is กรุงเทพ.".
            When generating new questions, if a student answers correctly, create a new question that is similar to the previous one. If a student answers incorrectly, generate a new question that is different from the previous one. Ensure the new question follows the same format as before.
            Track the student’s progress and adjust the difficulty of the questions accordingly. Provide more challenging questions if the student is performing well, and easier questions if the student is struggling. Only output the list of questions and feedback as described.
        """)
    return prompt
    # return SystemMessagePromptTemplate(prompt=prompt) 
    

def get_submit_question_prompt() -> str:
    prompt = PromptTemplate(
        input_variables=["student_answers"],
        template="""
            get the feedback and explanation for the student's answers for all student answer {student_answers} from the Thai teacher .
            The feedback should be array of json format like this e.g. ["id": 1, "feedback": "The correct answer is กรุงเทพ."].  
        """
    )
    return prompt
    # return HumanMessagePromptTemplate(prompt=prompt)


if not st.session_state.clicked:
    st.session_state.selected_categories = st.multiselect(
        "What topic would you like to learn?",
        ["Food", "Traval", "Education", "Health", "Technology", "Entertainment", "Sports"],
        [],
    )

if not st.session_state.clicked:
    st.button("Choose", disabled=st.session_state.selected_categories == [], on_click=choose_topic)

if st.session_state.clicked:
    for i, q in enumerate(st.session_state.questions):
        if f"question_{i}" not in st.session_state: 
            st.session_state[f"question_{i}"] = q["options"][0]  # Default to first option

        st.radio(
            q["question"],
            q["options"],
            key=f"radio_{i}",
            index=q["options"].index(st.session_state[f"question_{i}"]),
            on_change=select,
            args=(i,)
        )

        if st.session_state.feedback:
            st.write(st.session_state.feedback[i]["feedback"])
            st.write(f"Your answer: {st.session_state[f'radio_{i}']}")
        
    if st.session_state.feedback:
        st.button("Reset", on_click=reset)
    else:
        st.button("Submit", on_click=submit)
        
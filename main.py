from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
import json
import openai
import random
from os import environ as env
app = FastAPI()

origins = [
"http://localhost:3000/",
"http://localhost:8000/","*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Data(BaseModel):
    name:str 
    dob:str  
    race:str 
    gender:str
    height:str
    weight:str
    a1c:str   
    bp:str    
    medicine:str


@app.post("/")
async def data(data : Data):
    def pass_question(final_question):
        openai.api_key = env['MY_VARIABLE']
        completion = openai.Completion.create(
            model='text-davinci-003',
            prompt=final_question,
            max_tokens=1024,
            n=1,
            temperature=0.5,
            stop=None
            )
        response = completion.choices[0].text
        return response

    question1= pass_question(f"my prescription is {data.medicine} and my question is 'Are there any drug interactions I need to be aware of ?' explain in points")
    question2=pass_question(f"my prescription is {data.medicine} and my question is 'Is there any prescriptions I need to be really concerned with if added to my list?' explain in points")
    question3=pass_question(f"my prescription is {data.medicine} and my question is 'Are thee any medical symptoms I need to watch for when taking my prescriptions?' explain in points")
    question4=pass_question(f"my prescription is {data.medicine} and my question is 'Do I need to watch for any food-drug interactions based on my prescriptions?' explain in points")
    question5=pass_question(f"my prescription is {data.medicine} and my question is 'Are there any food I need to avoid ?' explain in points")
    question6=pass_question(f"my prescription is {data.medicine} and my question is 'Are there any food I need to consume based on my prescriptions ?' explain in points")


    dict_obj = {
            "name":data.name,
            "dob":data.dob,
            "race":data.race,
            "gender":data.gender,
            "height":data.height,
            "weight":data.weight,
            "a1c":data.a1c,
            "bp":data.bp,
            "medicine":data.medicine,
            "q1":' Are there any drug interactions I need to be aware of ?  \n'+question1,
            "q2":'Is there any prescriptions I need to be really concerned with if added to my list? \n'+question2,
            "q3":'Are thee any medical symptoms I need to watch for when taking my prescriptions? \n'+question3,
            "q4":'Do I need to watch for any food-drug interactions based on my prescriptions? \n'+question4,
            "q5":'Are there any food I need to avoid ? \n'+question5,
            "q6":'Are there any food I need to consume based on my prescriptions ? \n'+question6,
                }
    
    with open('user_data.json','w') as fp:
        json.dump(dict_obj, fp)
    return data


@app.get("/answer/")
async def send_answers(query:str):
    with open("user_data.json") as fp:
        ans = json.load(fp)
    f_ans = ans[query]
    return f_ans

# custom 

class Ques(BaseModel):
    que : str

@app.post("/prompt")
async def get_question(que : Ques):
    temp= que.__str__()
    temp = temp.split('=')
    with open('questions.json','w') as fp:
        json.dump(str(temp[1]), fp)
    return que




@app.get("/prompt/")
async def prompt(query: str):

    with open("user_data.json") as fp:
        data = json.load(fp)
    
    user_data = data['medicine']

    final_question = f"my prescription is {user_data} and my question is {query} explain in points"
    
    def pass_question(final_question):
        openai.api_key = env['MY_VARIABLE']
        completion = openai.Completion.create(
            model='text-davinci-003',
            prompt=final_question,
            max_tokens=1024,
            n=1,
            temperature=0.5,
            stop=None
            )
        response = completion.choices[0].text
        print(final_question)
        return response

    final_ans = pass_question(final_question)
    data[query] = str(query)+" \n"+str(final_ans)+" \n"+str(random.randint(0,100))

    with open('user_data.json','w') as fp:
        json.dump(data, fp)

    return final_ans




@app.get("/article/")
async def prompt(query: str):

    query_dict={
        "q7":"Display the Two most influential medical articles for me",
        "q8":"Display both articles as 100 words summaries",
        "q9":"Are there any clinical trials which would intrest me ?",
    }

    with open("user_data.json") as fp:
        data = json.load(fp)
        final_ans={'key':''}
    
    def pass_question(final_question):
        openai.api_key = env['MY_VARIABLE']
        completion = openai.Completion.create(
            model='text-davinci-003',
            prompt=final_question,
            max_tokens=1024,
            n=1,
            temperature=0.5,
            stop=None
            )
        response = completion.choices[0].text
        return response

    if query=="q8":
        qus = data["q7"]+" "+query_dict[query]
        final_ans['key']= pass_question(qus)
    
    elif query=="q7":
        final_ans['key'] = pass_question(query_dict[query])
        data['q7'] = final_ans['key']
        
    else:
        user_data = data['medicine'] +"\n"+data['weight']+"\n"+data['a1c']+"\n"+data['height']
        final_ans['key'] = pass_question(query_dict[query]+user_data)


    with open('user_data.json','w') as fp:
        json.dump(data, fp)

    return final_ans['key']

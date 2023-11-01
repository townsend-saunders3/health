import streamlit as st
import pandas as pd
import json
import utils
import openai
openai.api_key = st.secrets['api_key']
st.markdown("""
The goal of this script is to let someone know if they are deficient, on target, or in excess of certain micro or macro nutrients.
The entire app is AI driven so some information may not be accurate, due to model hallucination of information.  However, with time and the 
release of more accurate models, hopefully the factual health information will become accurate enough to help individuals with their diet

Overview
** There are two main objectives of this script
A. Get user information
    1. Get relevant health information on the user
    2. Extract daily nutrient goals for user based on relevant health info.  If none provided, use average human values.
B. Get information on user diet of current day.
    1. Get information on what the user ate.
    2. For each food that the user ate, break down into micro and macro nutrients
    3. Compare to daily nutrient values and give overview of excess, on target, and deficiencies
""")
#Might be useful to abstract to a class at a later time
# class Food(foodName, foodNutrients):
    

#Names of the nutrient files
def getNutrientNames():
    nutrientNames = [
        "aminos",
        "macro",
        "minerals",
        "other",
        "vitamins"
    ]
    return nutrientNames

# Retrieve all the json prompts from nutrients folder and store as nested python dictionary objects
def getNutrientPrompts(nutrientNames):
    nutrientPrompts = {}
    for nutrientName in nutrientNames:
        with open("nutrients/{}.json".format(nutrientName)) as file:
            nutrientPrompt = json.load(file)
        nutrientPrompts[nutrientName] = nutrientPrompt
    st.write(nutrientPrompts)
    return nutrientPrompts

# Get the nutrient break down of a given amount and unit of food using chatGPT
def getFoodNutrientResponse(food, nutrientPrompt):
    foodName, foodAmount, foodUnit = food
    promptText = "Can you fill in the following nutrientPrompt for {} {} of {}?  If unknown just fill with 'N/A'.  Do not return anything else besides the filled in json".format(foodAmount, foodUnit, foodName)
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": promptText +' ' +json.dumps(nutrientPrompt)}
        ]
    )
    return completion.choices[0].message['content']

# Break down natural language repsonse of food that user ate into a iterable python object
def getFoodList(whatTheyAte):
    promptText = """
    Can you split the following response into a list of foods.  The list should be an iterable python list of tuples 
    where the first element in the tuple is the name of the food, the second element is the amount of food eaten, 
    and the third element is the ueit of the amount eaten.  Convert to standard metric units if possible.
    """
    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role" : "user", "content": promptText + ' ' + whatTheyAte}
        ]
        )
    return eval(completion.choices[0].message['content'])

# Get the the nutrient breakdowns for an individual food
def getFoodNutrientResponses(food, nutrientPrompts):
    foodNutrientResponses = {}
    for nutrientName in nutrientPrompts.keys():
        nutrientPrompt = nutrientPrompts[nutrientName]
        foodNutrientResponse = getFoodNutrientResponse(food, nutrientPrompt)
        foodNutrientResponses[nutrientName] = foodNutrientResponse
        # st.write(foodNutrientResponse)
    return foodNutrientResponses
    
# Get all the nutrient breakdowns for all foods in a given list.
def getFoodNutrients(foodList, nutrientPrompts):
    foodNutrients = {}
    for food in foodList:
        foodName = food[0]
        foodNutrientResponses = getFoodNutrientResponses(food, nutrientPrompts)
        foodObject = {}
        foodObject["Food Name"] = food[0]
        foodObject["Food Amount"] = food[1]
        foodObject["Food Unit"] = food[2]
        foodObject['Nutrients'] = foodNutrientResponses
        foodNutrients[foodName] = foodObject

# Get a the target nutrients for a user given their health bio and an individual nutrient prompt
def getNutrientHealthResponse(healthBio, nutrientPrompt):
    height, weight, age, sex = healthBio
    promptText = "Can you fill in the following nutrient profile for an individual of weight {}, height {}, age {}, and sex {}?  We want the average daily goals. If unknown just fill with 'N/A'.  Do not return anything else besides the filled in json".format(weight, height, age, sex)
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": promptText +' ' +json.dumps(nutrientPrompt)}
        ]
    )
    return completion.choices[0].message['content']

# Get the target nutrients for a user given their health bio and a dictionary of nutrient prompts.  Returns a dictionary of nutrient responses
def getNutrientHealthResponses(healthBio, nutrientPrompts):
    nutrientHealthResponses = {}
    for nutrientName in nutrientPrompts.keys():
        print(nutrientName)
        nutrientPrompt = nutrientPrompts[nutrientName]
        nutrientHealthResponse = getNutrientHealthResponse(healthBio, nutrientPrompt)
        nutrientHealthResponses[nutrientName] = nutrientHealthResponse
        # st.write(nutrientHealthResponse)
    return nutrientHealthResponses
        

# Get the target nutrients for a user given their health bio and a dictionary of nutrient prompts.  Returns a user nutrient object
def getUserNutrients(healthBio, nutrientPrompts):
    userNutrients = {}
    height, weight, age, sex = healthBio
    userNutrients['Height'] = height
    userNutrients['Weight'] = weight
    userNutrients['Age'] = age
    userNutrients['Sex'] = sex
    nutrientHealthResponses = getNutrientHealthResponses(healthBio, nutrientPrompts)
    userNutrients['Nutrients'] = nutrientHealthResponses
        

def main():
    with st.sidebar:
        st.title("Health Data")
        with st.form('Individual Heath'):
            height = st.number_input("Height (inches)")
            weight = st.number_input('Weight (Lbs)')
            age = st.number_input("Age (Years)")
            sex = st.multiselect('Sex', ['Male', 'Female'])
            st.write("Put the form here")
            healthSubmit = st.form_submit_button()
    
    healthBio = (height, weight, age, sex)
    st.title("Food Log")
    with st.form('Food Log'):
        st.caption('Please enter your meal(s)')
        whatTheyAte = st.text_input('Enter your meals today')
        logSubmit = st.form_submit_button()
    if whatTheyAte:
        foodList = getFoodList(whatTheyAte)
        st.write(foodList)
        nutrientNames = getNutrientNames()
        nutrientPrompts = getNutrientPrompts(nutrientNames)
        foodNutrients = getFoodNutrients(foodList, nutrientPrompts)
        userNutrients = getUserNutrients(healthBio, nutrientPrompts)
        st.json(nutrientPrompts)
        st.json(foodNutrients)
        st.json(userNutrients)

main()

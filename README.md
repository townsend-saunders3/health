# health

This is an application to get the full nutrient breakdown of any type of food using openai gpt4.

To test out this application, clone the repo then in your terminal run 
  streamlit run "Health Home.py"

Make sure to add your openai api key to Health Home.py

Once a food has been entered into the text box, the script sends 5 queries to the gpt model of your choosing.  Each query asks for the amion acid, macronutrient, minerals, other, and vitamin breakdown of the food group provided in the query.

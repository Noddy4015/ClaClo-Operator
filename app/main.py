from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from urllib.parse import quote_plus
import urllib.parse
import json
from fastapi import FastAPI, Query
from fastapi import FastAPI, Body
from statistics import mean, median, stdev
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import numpy as np
import nltk
nltk.download('vader_lexicon')
from fastapi import Form
from datetime import datetime, timedelta
from routes import router

app = FastAPI()

# Include routes from other modules
app.include_router(router)








    



    






    



    




    


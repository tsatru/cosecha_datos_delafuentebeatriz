#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 12:12:30 2020

@author: tania
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import requests as req
import csv
import urllib2
import re
import lxml
from sqlalchemy import create_engine
import psycopg2
from selenium.common.exceptions import NoSuchElementException
import unicodedata

pg_engine='postgresql+psycopg2://localhost:5432/colecciones'


faltantes = pd.read_sql_query("SELECT DISTINCT nombre_busqueda FROM iie_afmt_cbf.revision_faltantes_iie_afmt_cbf_ts WHERE nombre_busqueda IS NOT NULL", pg_engine)
faltantes_list = faltantes['filename_we'].values.tolist()

index = 0


while index < len(faltantes_list):
    moon = faltantes_list[index]
    print( moon )
    driver = webdriver.Firefox()

    driver.get('https://artdossier.esteticas.unam.mx/index.php/fondo-beatriz-de-la-fuente')
    search = driver.find_element_by_name('query')
    search.clear()
    search.send_keys(moon)
    search = driver.find_element_by_xpath('/html/body/header/div/div[2]/form/button').click()
    result = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div[2]/article/div[1]/a/div').click()
    titulo_pag = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/h1').text
    currenturl =  driver.current_url

    resp = req.get(currenturl)

    soup = BeautifulSoup(resp.text, 'html.parser')

    results = soup.find_all("div", {"class": "field"})



    ficha = pd.DataFrame()

    ficha['campos'] = [soup.find(re.compile(r'h\d+')).text  for soup in results]

    ficha['contenido'] = [soup.find('div').text.strip('\s+') for soup in results]

    ficha['contenido'] = ficha['contenido'].str.strip() 

    ficha.set_index('campos', inplace=True)

    ficha_transpose = ficha.transpose()
    ficha_transpose['titulo_pag'] = titulo_pag
    
    ficha_transpose.to_csv(moon, encoding='utf-8') 
    driver.quit()
    

    index = index + 1
    

    except NoSuchElementException as e:
        print('Error when trying to perform do_here_what_can_cause_IOError: %s', e)

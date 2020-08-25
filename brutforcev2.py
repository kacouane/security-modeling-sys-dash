import pandas as pa
import numpy as np
import time
import datetime
from threading import Lock, Thread
import os
dataset = pa.read_csv('/home/antoine/Documents/GDrive/CFI_survey/test excel/Survey_Compare_Tab-database.csv')

#
#   use Technologie name as unique key to select a row
#
Master_key_Column = 'Technology'
dataset['id'] = dataset[Master_key_Column]
dataset.set_index('id', inplace=True, drop=False)

#
#   create a header with links linking to tech paper
#
dataset['Protections'] = '['+dataset['id']+']('+dataset['reference paper']+')'


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       Globals                                 #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

Header_Column = 'Protections'
Hidden_Columns = ['id','reference paper',Master_key_Column,Header_Column]
Cost_input_Columns = ['Cost memory','cost in process','Cost runtime']
Total_Cost_Column = 'total cost'
Attack_List = dataset.columns[2:22]
Protection_list = list(dataset[Master_key_Column])

def return_coverage(selection,database):
    subdata = pa.DataFrame(database,columns=[ i for i in dataset.columns])
    selection_database = subdata.query(Master_key_Column+' in '+str(selection))
    list_of_coverage = list(selection_database[column].astype('int64').max() for column in Attack_List)
    if len(list_of_coverage) != 0 :
        ret = (sum(list_of_coverage)/len(list_of_coverage))*100
    else :
        ret = 1
    return ret

def return_cost(selection,database):
    subdata = pa.DataFrame(database,columns=[ i for i in dataset.columns])
    selection_database = subdata.query(Master_key_Column+' in '+str(selection))
    a = selection_database[Total_Cost_Column].sum()
    if a == 0:
        a = 1
    return(a)


def prepare_imput(database,tech_list,binarray):

    selection_generated = []
    increment = 0
    for i in binarray:
        if i == '1':
            selection_generated.append(tech_list[increment])
        increment +=1
    return selection_generated

old = pa.read_csv('fusy_test_for_brute.csv') 
old = old.drop(columns=['Unnamed: 0'])
f = open("brute_persist.txt", "r")
lastchecked = int(f.readline())
f.close()
for j in range(1000):
    print('start dataset generation at ',lastchecked)
    t1 = time.time()
    selection_input = []
    i=0
    while i < 2000:
        if(16777215 <=lastchecked ):
            print('finished')
            break
        # print('lastchecked :',bin(lastchecked)[2:])
        input_prepared = prepare_imput(dataset,Protection_list,bin(lastchecked)[2:])
        tut= list(old.query('techs'+' == \"'+str(input_prepared)+'\"')['techs'])#[old['techs'] == str(input_prepared)]['techs'])
        #print(tut)
        if tut == []:
            selection_input.append(str(input_prepared))
            i+=1
            print('.',end='',flush=True)
        else :
            print('-',end='',flush=True)
        lastchecked+=1


    data = {
        'techs': selection_input,
        'cost': list(return_cost(select,dataset) for select in selection_input),
        'coverage': list(return_coverage(select,dataset) for select in selection_input)
    }
    df = pa.DataFrame(data=data)
    

    df['coverage_over_cost'] = df['coverage']/df['cost']
    def tu(x):
        return len((str(x)).split(','))
    df['nb_tech_used'] = df['techs'].apply(tu)

    print('complete\n')
    print('merging with database ...')
    # old = pa.read_csv('fusy_test_for_brute.csv') 

    

    old = pa.concat([df,old]).reset_index(drop=True)

    #print(df.tail(5))
    datasize = int(old.size/5)
    remaining = 16777216-datasize
    print('database size is now : '+ str(f"{datasize:,d}"),'remaining ',f"{remaining:,d}")
    print('\n')
    print('=================================================')
    print('saving dataset nb '+str(j)+' to file ... ',end='',flush=True)
    old.to_csv('fusy_test_for_brute.csv') 
    f = open("brute_persist.txt", "w")
    f.write(str(lastchecked))
    f.close() 
    print('complete')
    print('=================================================')
    t2 = time.time()
    print('test took ',(t2-t1),'s remaining estimated time = ',datetime.timedelta(seconds=((t2-t1)*remaining/2000)),'\n'       )
    
    time.sleep(2)

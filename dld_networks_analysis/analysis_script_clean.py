import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import json

my_sheets = [
    "(1) Matrix_Reasoning",
    "(2) Modified_Token_Test_NEW",
    "(2) Modified_Token_Test",
    "(3) Word Definitions",
    "(4) Spelling_Test",
    "(6) Digit_Span",
    "(5) Verbal_Fluency",
    "(7) Language_Production",
    "(9) Recalling_Sentences",
    "(11) N-Back",
]

#index of the column tbat contains the 'score', for each sheet
score_indices=[2,2,3,3,4,None,None,5,8] #process using try: lambda x: try: int(x[score])
# print(len(score_indices))


def process_excel_files(folder_path):
    # # Get all .xlsx files
    xlsx_files = list(folder_path.glob("*.xlsx"))

    # # List to collect processed DataFrames
    final_df = pd.DataFrame()

    for file_path in xlsx_files:
    # Load all sheets from the current Excel file
        sheets = pd.read_excel(file_path, sheet_name=None)  # returns dict {sheet_name: DataFrame}
        sheets = {name: df for name, df in sheets.items() if name in my_sheets}
        if len(sheets)>9: #some of the sheets are named, ordered, or formatted differently
            sheets.pop("(2) Modified_Token_Test", None)
        all_sheets_df = pd.DataFrame()
        for ind, (sheet_name, df) in enumerate(sheets.items()):
            #variables for digit span
            forward = None
            backward = None
            # df = df.dropna(how="all")  # remove empty rows
            # df["source_file"] = file_path.name
            # df["sheet_name"] = sheet_name

            # if there is a 'score' column, try to grab it
            if score_indices[ind] !=None:
                try:
                    numeric_vals = pd.to_numeric(df.iloc[:,score_indices[ind]], errors="coerce")
                except Exception as e:
                    try:
                        numeric_vals = pd.to_numeric(df.iloc[:,7], errors="coerce") #nback score is one col to the left sometimes :( 
                    except Exception as e:
                        print(sheet_name)
                        print(file_path.name)
                        print(df)
                # special cases for nback and digit span tasks
                if sheet_name=='(11) N-Back':
                    score_sum = numeric_vals.sum()
                elif sheet_name=='(6) Digit_Span':
                    forward = numeric_vals.iloc[18]
                    backward = numeric_vals.iloc[-1]
                    all_sheets_df=pd.concat([all_sheets_df,pd.DataFrame({'src':file_path.name,'task':['ds_forward'],'score_sum':[forward]}) ])
                    all_sheets_df=pd.concat([all_sheets_df,pd.DataFrame({'src':file_path.name,'task':['ds_backward'],'score_sum':[backward]}) ])
                    continue
                else:
                    score_sum = numeric_vals.iloc[-1]
            else:
                score_sum=None # for verbal fluency and lang production
            # Append to our list
            all_sheets_df=pd.concat([all_sheets_df,pd.DataFrame({'src':file_path.name,'task':[sheet_name],'score_sum':[score_sum]}) ])
        wide_df = all_sheets_df.pivot(index="src", columns="task", values="score_sum")
        wide_df.index.name = None
        wide_df.columns.name = None
        
        final_df = pd.concat([final_df,wide_df])
        return final_df


#run the process_excel_files function on the both the dld and td scored assessments folders
folder_path_dld = Path("scored assessments_dld")
folder_path_td = Path("scored assessments_td")

final_df_dld = process_excel_files(folder_path_dld)
final_df_td = process_excel_files(folder_path_td)

#save to separate csvs if you would like
final_df_td.to_csv('td_summary.csv',index=False)
final_df_dld.to_csv('dld_summary.csv',index=False)

#get dataframes ready to be combined
final_df_dld['pop']='dld' #add population column
final_df_td['pop']='td'

#the dld dataset has missing values for this sheet, and needs to match the td set in naming/format, so this line fixes it
final_df_dld['(2) Modified_Token_Test_NEW'] = final_df_dld.iloc[:, 2].fillna(final_df_dld.iloc[:, -2])

final_df_dld.drop(['(2) Modified_Token_Test'],inplace=True,axis=1)

#combine our datasets
final_df=pd.concat([final_df_dld,final_df_td])
final_df['id'] = final_df.index

final_df.reset_index(drop=True,inplace=True)
#clean all ids from filenames
final_df['id']=final_df['id'].apply(lambda x: x.split('_Assessment')[0])
final_df['id']=final_df['id'].apply(lambda x: x.split('Sub')[-1])
final_df['id']=final_df['id'].apply(lambda x: x.split('_assessment.xlsx')[0])
final_df['id']=final_df['id'].apply(lambda x: x.split('sub')[-1])
final_df['id']=final_df['id'].apply(lambda x: x.split('_')[-1])
final_df['id']=final_df['id'].apply(lambda x: x.split('Assessment')[0])
final_df['id']=final_df['id'].apply(lambda x: x.split('.xlsx')[0])

#load in and clean demographics file
demo = pd.read_csv('DLD+lang+screener_August+13,+2025_11.40.csv')
demo = demo[demo.Q18.isin(final_df.id)] #match prolific ids to filter the demo file
demo.drop_duplicates(subset='Q18',keep='first',inplace=True)

#sort demo file and final_df by id
demo = demo.sort_values(by='Q18')
final_df = final_df.sort_values(by='id')


def score_touch_times(csv_folder):
    # Touch the squares slowly and the circles quickly. - original instructions
    # score 1 if squares time is greater than circles time

    comparison_df = pd.DataFrame()
    for root, dirs, files in os.walk(csv_folder):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)

                parsed_data = ast.literal_eval(df.iloc[11].moves)

                tdf = pd.DataFrame(parsed_data)
                score=0
                id=file_path.split('\\')[-1].split('.csv')[0]
                if len(tdf.columns)>0:
                    tdf = tdf[['src', 'start', 'end']]
                    squares=0
                    circles=0
                    for _,row in tdf.iterrows():
                        if "circle" in row.src:
                            circles+= row.end - row.start
                        elif "square" in row.src:
                            squares+= row.end - row.start
                    if squares>circles:
                        score=1
                comparison_df=pd.concat([comparison_df, pd.DataFrame({'score':score,'id':id}, index=[0])])
                
    return comparison_df

#score the "quickly/slowly" touch time tasks for both datasets
comparison_df_td=score_touch_times('scored csvs_td')
comparison_df_dld=score_touch_times('scored csvs_dld')
#combine and sort by prolific id, now matching final_df and the demographics file
comparison_df=pd.concat([comparison_df_td,comparison_df_dld])
comparison_df=comparison_df.sort_values(by='id')

#insert the touch time scores into our final_df
new_scores=[]
for prev_total, addition in zip(final_df.iloc[:,2], comparison_df.score):
    try:
        new_scores.append(prev_total+addition)
    except Exception as e:
        new_scores.append(pd.NA)
final_df.iloc[:,2]=new_scores

#start combining final_df and demographics file
final_df.reset_index(drop=True,inplace=True)
demo.reset_index(drop=True,inplace=True)
final_df['age']=demo.Q1
final_df['education']=demo.Q3

#final df with all scores and some relevant demographics
final_df.to_csv('full_summary.csv',index=False)

#save full demo file separately if you would like
demo.to_csv('filtered_demo.csv',index=False)
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import datetime as dt
import numpy as np
import base64
app = dash.Dash(__name__)
server=app.server



data= pd.read_csv("https://raw.githubusercontent.com/adityanarayanan3101/projectplot/master/SPX_factors.csv")
data['Date']= pd.to_datetime(data['Date'],format='%m/%d/%Y')


dict_list= [{'value': i,'label': i} for i in list(data.iloc[:,1:].columns)]

image= "UCLA_Anderson.png"
test_base64 = base64.b64encode(open(image, 'rb').read()).decode('ascii')

fig= px.line(data,x=data.columns[0],y=data.columns[1:])
app.layout= html.Div([html.H1('Project for Prof. Chernov and Prof. Augustin',style={'font-family':'calibri','color':'black','font-size':'24pt','border-bottom-style': 'dotted'}),\
            html.Img(src='data:image/png;base64,{}'.format(test_base64),style={'position':'absolute','right':'0','top':'0','hieght':'10%','width':'20%'}),\
            
        html.Div([
                 html.H2('Choose Time series:',style={'font-family':'calibri','font-size':'14pt'}),\
                dcc.Dropdown(id= 'Time series',\
                options=dict_list, multi=True,style={'font-family':'calibri'}),\
                dcc.DatePickerRange(id='SE dates',min_date_allowed= data['Date'].min(),max_date_allowed= data['Date'].max(), style={'margin-top':'10%'}),
                dcc.Checklist(id='Returns',options=[{'value':'True','label':'Returns'}],style={'font-family':'calibri','margin-top':'10%'}),
                dcc.Dropdown(id='Return Frequency',options=[{'value':1,'label':'1 day'},{'value':5,'label':'1 week'},{'value':20,'label':'1 month'}],style={'float':'center','font-family':'calibri','display': 'none'},placeholder="Select frequency of return"),\
                dcc.Checklist(id='subplots',options=[{'value':'True','label':'Sub-plots'}],style={'font-family':'calibri','margin-top':'10%'}),\
                dcc.Dropdown(id='Subplot-type',options=[{'value':1,'label':'For each series'},{'value':2,'label':'By a field'}],style={'float':'center','font-family':'calibri','display': 'none'}, placeholder='How do you want to subset?'),\
                dcc.Dropdown(id= 'Series-idX',options=[{'value': i,'label': i} for i in list(data.iloc[:,1:].columns)],style={'float':'center','font-family':'calibri','display': 'none'},placeholder='Series X'),\
                dcc.Dropdown(id= 'Series-idY',options=[{'value': i,'label': i} for i in list(data.iloc[:,1:].columns)],style={'float':'center','font-family':'calibri','display': 'none'},placeholder='Series Y')
                
                ],style={'width': '20%', 'display': 'inline-block','border-style': 'outset'}),dcc.Graph(id="fig1",figure=fig, style={'float':'right','display':'inline-block','border-style': 'outset','marginRight':'10%', 'width':'50%'})],\
                style={'width': '100%', 'display': 'inline-block'})

##Area for common transformations, please ensure data is exptracted in a all weekday format
def ret_trans(df,cols,freq):
    #df is a dataframe and cols is list. Func is a lambda function.
    if freq== 1:
        for i in cols:
            df[i]= np.log(df[i])-np.log(df[i].shift(freq))
        return df.dropna()
    elif freq==5:
        for i in cols:
            df[i]= np.log(df[i])-np.log(df[i].shift(freq))
            df['day']= df['Date'].dt.dayofweek
        df= df[df['day']==2]
        return df.drop(['day'],axis=1)
    
    elif freq==20:
        for i in cols:
            df[i]= 1+np.log(df[i])-np.log(df[i].shift(1))
    
        df['Month']= df['Date'].dt.month
        df['Year']= df['Date'].dt.year
        data= df.groupby(['Month','Year'])[cols].prod()
        data=data-1
        data=data.reset_index()
        data['Month']= data['Month'].astype(str)
        data['Year']= data['Year'].astype(str)
        data['Date']= data['Month']+data['Year']
        data['Date']= pd.to_datetime(data['Date'],format= '%m%Y')+pd.tseries.offsets.MonthEnd(1)
        data= data.set_index('Date')
        
        df= df.sort_values(by='Date').reset_index()
        
        
        data= data.reset_index()
        data= data.sort_values(by='Date')
        data= data.set_index(['Month','Year'])
        df['Month']= df['Month'].diff()
        df= df.iloc[np.maximum(np.where(df['Month'].dropna().values!=0)[0],0),:]
        df['Month']= df['Date'].dt.month
        df['Month']= df['Month'].astype(str)
        df['Year']= df['Year'].astype(str)
        df= df.drop(['Date']+cols, axis=1)
        
        df= df.set_index(['Month','Year']).iloc[:,1:]
        data= pd.merge(data,df,left_index=True,right_index=True)
        return data.sort_values('Date')
    
def replot_figure(cache_data=data):
    f1= px.line(cache_data,x=cache_data.columns[0],y=cache_data.columns[1:])
    return f1

def create_subplots(cache_data):
    fig = make_subplots(rows=5, cols=2)
    r=1
    for i in range(1,11,1):
        c=1
        
        if i%2==0:
            c=2

        cd= cache_data[cache_data['Decile']==i]
        layout= go.Layout(autosize=False,width=500, height=500)
        gs= go.Scatter(x= cd.iloc[:,2], y= cd.iloc[:,1], mode= 'markers',name= 'Decile '+str(i))
        fig.append_trace(gs, row=r,col=c)
        if i%2==0:
            r=r+1
        
    return fig
        
    
    pass

    
    

@app.callback(
   Output(component_id='Subplot-type', component_property='style'),
   [Input(component_id='subplots', component_property='value')])
def hide_element(visibility_state):
    
    if visibility_state== ['True']:
        
        return {'float':'center','font-family':'calibri','display': 'block'}
    else:
        return {'float':'center','font-family':'calibri','display': 'none'}
         
@app.callback(
   [Output(component_id='Series-idX', component_property='style'),Output(component_id='Series-idY', component_property='style')],
   [Input(component_id='subplots', component_property='value'),Input(component_id='Subplot-type', component_property='value')])
def hide_element1(visibility_state,sbt):
    
    if visibility_state==['True'] and sbt==2 :
        
        return [{'float':'center','font-family':'calibri','display': 'block'},{'float':'center','font-family':'calibri','display': 'block'}]
    else:
        return [{'float':'center','font-family':'calibri','display': 'none'},{'float':'center','font-family':'calibri','display': 'none'}]
        
@app.callback(
   Output(component_id='Return Frequency', component_property='style'),
   [Input(component_id='Returns', component_property='value')])

def show_hide_element(visibility_state):

    if visibility_state== ['True']:
        return {'float':'center','font-family':'calibri','display': 'block'}
    else:
        return {'float':'center','font-family':'calibri','display': 'none'}
        

@app.callback(
   Output(component_id='fig1', component_property='figure'),\
   [Input(component_id='Returns', component_property='value'),Input(component_id='Return Frequency', \
    component_property='value'),Input(component_id='SE dates', component_property='start_date'),\
    Input(component_id='SE dates', component_property='end_date'),Input(component_id='subplots', component_property='value'),\
    Input(component_id='Subplot-type', component_property='value'),Input(component_id='Series-idX', component_property='value'),Input(component_id='Series-idY', component_property='value'),Input(component_id='Time series', component_property='value')])

def update_plot(ret,ret_freq,start_date,end_date,subplot_state,subplot_type,sx,sy, init_val):
    
    cache_data= data
    fig_changed= replot_figure(cache_data)
    print("Update Function Entered")
    
    if init_val is not None:
        cache_data= cache_data[['Date']+init_val]
        fig_changed= replot_figure(cache_data)
    
    if ret==['True'] and ret_freq is not None:
        
        cache_data= ret_trans(cache_data,init_val, ret_freq)
        fig_changed= replot_figure(cache_data)
        print(cache_data)
    else:
        pass
        
    if start_date is not None:
        
        cache_data= cache_data[cache_data['Date']>=start_date]
        fig_changed= replot_figure(cache_data)
        
    else:
        pass
    
    if end_date is not None:
        
        cache_data= cache_data[cache_data['Date']<=end_date]
        fig_changed= replot_figure(cache_data)
    else:
        pass
         
    if subplot_state==['True']:
        
            if subplot_type==2:
                if sx is not None and sy is not None:
                #print('Entered')
                    cache_data= cache_data.set_index('Date')
                    cache_data= cache_data.reset_index()
                    cache_data= cache_data.iloc[:,[0]+[np.where(sy==cache_data.columns)[0][0]]+[np.where(sx==cache_data.columns)[0][0]]]
                    #print(cache_data)
                    
                    #print(cache_data.iloc[:,2])
                    cache_data['Decile']= pd.qcut(cache_data.iloc[:,2].rank(method='first'),10,labels= list(range(1,11,1)))
                    #fig_changed= px.scatter(cache_data,x= cache_data.columns[2], y=cache_data.columns[1],facet_col='Decile',width=1000, height=1000,trendline="ols")
                    #fig_changed.update_layout(autosize=False,width=5000,height=500)
                    fig_changed= create_subplots(cache_data)
                    return fig_changed

            else:
                
                fig_changed= replot_figure(cache_data)
                return fig_changed
            
            
        
    else:
        pass
    
    return fig_changed
        



if __name__== '__main__':
    app.run_server(debug= True,use_reloader=False)

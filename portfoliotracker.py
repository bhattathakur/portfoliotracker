import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import pytz
from io import StringIO


st.set_page_config(layout='wide')


#functions
def color_val(val):
   if val>0:return "color:green;"
   return "color:red;"

# Function to alternate row colors
def alternating_row_colors(row):
    return ['background-color: #F2F2F2' if row.name % 2 == 0 else 'background-color: white'] * len(row)

#style dict
style_dict = {
    'text-align': 'center',
    'font-family': 'Courier,monospace',
    'font-size': '16px',
   #'font-weight': 'bold',
    'color': 'magenta',
   # 'background-color': '#f0f0f0',
    'border': '0.5px solid black',
    #'border-radius': '5px',
    'padding': '5px'
}


#introcude tabs
tab1,tab2,tab3=st.tabs(["Portfolio Overview","Per Minute Portfolio Change","Daily Portfolio Change"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:

        st.markdown("✍️ **Manually enter your portfolio:** (One line per stock in format: `Ticker, Shares, Price`)")
        with st.form("Ticker Information Input"):
            txt_area = st.text_area("", placeholder='AAPL,20,200',value='AAPL,300,200 \nNVDA,200,100\nTSLA,50,250')
            submitted = st.form_submit_button("SUBMIT")
        st.markdown("**OR**")
        st.markdown("📁 **Upload a CSV file** including your portfolio (one stock per line in format (INCLUDING THE HEADER): `Ticker, Shares, Price`) as an exampble below:")
        st.text(" Ticker, Shares, Price \n AAPL,300,200\n NVDA,200,100\
        ")
        file_uploaded = st.file_uploader("Choose a CSV file", type="csv")
        st.markdown("---")


        #submitted=True

        df = None  # Initialize dataframe

        # Case 1: Both inputs used — show error
        if file_uploaded and submitted and txt_area.strip():
            st.error("❌ Please use either the file upload or manual input, not both.")
        
        # Case 2: File uploaded
        elif file_uploaded:
            try:
                df = pd.read_csv(file_uploaded)
                st.success("✅ File uploaded successfully.")
                df['Shares'] = pd.to_numeric(df['Shares'], errors='coerce')
                df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
                df.dropna(inplace=True)
                df['TotalCost'] = df['Shares'] * df['Price']
                #st.write(df)
            except Exception as e:
                st.error(f"Error reading file: {e}")

        # Case 3: Manual input
        elif submitted:
            lines = txt_area.strip().split("\n")
            main_list = []
            st.write("You entered:")
            for i, line in enumerate(lines):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) != 3:
                    st.warning(f"⚠️ Invalid input on line {i+1}: `{line}`")
                    continue
                main_list.append(parts)
                st.write(f"{i+1}: {line}")
            
            if main_list:
                try:
                    df = pd.DataFrame(main_list, columns=['Ticker', 'Shares', 'Price'])
                    df['Shares'] = pd.to_numeric(df['Shares'], errors='coerce')
                    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
                    df.dropna(inplace=True)
                    df['TotalCost'] = df['Shares'] * df['Price']
                    #st.write(df)
                except Exception as e:
                    st.error(f"Error processing input: {e}")
            else:
                st.warning("No valid data entered.")
    #stop if no dataframe
    # if not submitted:
        if df is None or len(df)<1:st.stop()

        df.index=range(1,len(df)+1)
        #df.index.name='S.N.'

        df_fin = (
        df.style
        .format("{:.2f}", subset=df.select_dtypes(include=["float64"]).columns)
        #.apply(lambda row:row.apply(color_val), subset=["return(%)", "mean_return(%)"],axis=1)
        .apply(alternating_row_colors,axis=1)
        .set_properties(**style_dict)
        )
        html_table=df_fin.to_html(index=False)
        #st.write(df)
        centered_table = f"""
    <div style="display: flex; justify-content: center;">
        {html_table}
    </div>
    """
        #st.markdown(df_fin.to_html(),unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center;color:magenta;font-weight:bold;font-family:monospace;font-size:35px'>RAW INPUT PORTFOLIO</h2>",unsafe_allow_html=True)
        #st.markdown("Your Raw Input")
        st.markdown(centered_table,unsafe_allow_html=True)
        #st.table(df)

    # df['Shares'] = pd.to_numeric(df['Shares'], errors='coerce')
    # df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    # df.dropna(inplace=True)
    # df['TotalCost'] = df['Shares'] * df['Price']
    with col2:
        if df is not None and not df.empty:
            df_group = df.groupby('Ticker', as_index=False).agg({
                'Shares': 'sum',
                'TotalCost': 'sum'
            })
            df_group['AvgCost'] = df_group['TotalCost'] / df_group['Shares']

            st.markdown(f"<h2 style='text-align:center;color:magenta;font-weight:bold;font-family:monospace;font-size:35px'>AGGREGATED PORTFOLIO</h2>",unsafe_allow_html=True)


            #st.subheader("📊 Aggregated Portfolio")
            df_group.index=range(1,len(df_group)+1)
            #df_group.index.name='S.N.'

            group_fin= (
            df_group.style
            .format("{:.2f}", subset=df_group.select_dtypes(include=["float64"]).columns)
            #.apply(lambda row:row.apply(color_val), subset=["return(%)", "mean_return(%)"],axis=1)
            .apply(alternating_row_colors,axis=1)
            .set_properties(**style_dict)
            )


            #st.write(group_fin)
            html_table1=group_fin.to_html(index=False)
            centered_table1 = f"""
    <div style="display: flex; justify-content: center;">
        {html_table1}
    </div>
    """
            st.markdown(centered_table1,unsafe_allow_html=True)
            #st.markdown(group_fin.to_html(),unsafe_allow_html=True)
            fig = px.pie(df_group, values='TotalCost', names='Ticker', title='')
            fig.update_traces(textinfo='percent+label')
            fig.update_layout(
                title={
                    'text': "Investment Portfolio",
                    'x': 0.5,
                    'xanchor': 'center'
                },
                height=600,
                width=600
            )
            st.plotly_chart(fig)

            #bar diagram for the number of shares
            bar_fig=px.bar(df_group,x='Ticker',y='Shares',text_auto='.2s')


            bar_fig.update_layout(
                title={
                    'text': "Number of Shares in Portfolio",
                    'x': 0.5,
                    'xanchor': 'center'
                }
            )

            st.plotly_chart(bar_fig)


with tab2:
    #download yahoo data 

    debug=False

    tickers=list(df_group.Ticker)
    org_tickers=list(df_group.Ticker)
    if debug:st.write(f"Tickers: {tickers}")


    #yf data
    try:
        data=yf.download(tickers=tickers,interval='1m',group_by='tickers')

    except:
        st.error("Error occured during the data donwllaod from YFinance ... stop the app")
        st.stop()


    if debug:st.dataframe(data)

    #columns of dataframe
    #col_names=data.columns.to_list()
    #st.write(f"col_names: {col_names}")

    #if dataframe is empty
    if data.empty:
        st.error("Dataframe is empty ... stopping the app")
        st.stop()

    data.index=data.index.tz_convert("US/Eastern")

    data_index=pd.to_datetime(data.index)#.date
    d=np.unique(data.index.date)

    unique_dates=data.index.normalize().unique()#np.unique(data_index)
    if debug:st.write(f"unique_dates: {unique_dates.date}")

    #if st.session_state.get("active_tab")=="Per Minute Portfolio Change":
    #    with st.sidebar:
    #        date_radio=st.radio('Select a date',d[::-1])
    #date_radio=st.radio('Select a date',unique_dates)
    date_radio=st.radio('Select a date',d[::-1])


    #daily df
    #daily_df=data[data.index.normalize()==date_radio]
    daily_df=data[data.index.date==date_radio]

    daily_df.index=daily_df.index.strftime("%m/%d-%H:%M")
    #give index name as 'Datetime' if it is not an index as for some random generated multiple text it is not showing 'Datetime' in index and remaining part of the code is not working
    if daily_df.index.name!='Datetime':daily_df.index.name='Datetime'
    if debug:st.dataframe(daily_df)

    for ticker in daily_df.columns.levels[0]:
        #st.write(f"data frame for {ticker}")
        #ticker_df=data[ticker]
        ticker_df=daily_df[ticker]

        #include the number of shares
        #dates
        portfolio_ticker_info=df_group[df_group['Ticker']==ticker]
        portfolio_ticker_num=portfolio_ticker_info['Shares'].values
        portfolio_ticker_investement=portfolio_ticker_info['TotalCost'].values[0]
    

        daily_df[(ticker,'TotalShares')]=[portfolio_ticker_num]*len(daily_df)#portfolio_ticker_info['Shares'].values*ticker_df['Close']
        daily_df[(ticker,'Investment')]=portfolio_ticker_investement#*len(daily_df)#portfolio_ticker_info['Shares'].values*ticker_df['Close']
        daily_df[(ticker,'MarketValue')]=portfolio_ticker_info['Shares'].values*ticker_df['Close']
        daily_df[(ticker,'Volume')]= round(daily_df[(ticker,'Volume')]/1e6,3)#volume into million

        #find the returns
        daily_df[(ticker,'Return%')]=100*daily_df[ticker]['Close'].pct_change()
        #st.write(f"portfolio ticker info: {portfolio_ticker_info}")

    
    daily_df=daily_df.sort_index(axis=1)
    debug=False
    if debug:st.write(f"index and column names:\n{daily_df.columns}\n{daily_df.index}")
    if debug:st.dataframe(daily_df)

    #get the investment and total column
    market_value=daily_df.xs('MarketValue',axis=1,level=1)
    total_invest=daily_df.xs('Investment',axis=1,level=1)
    #st.dataframe(market_value)
    #st.dataframe(total_invest)

    #add total market value and total invesetment
    daily_df[('Total','MarketValue')]=market_value.sum(axis=1)
    daily_df[('Total','Investment')]=total_invest.sum(axis=1)

    debug=False

    if debug:
        st.dataframe(daily_df)
        st.write(f"columns: {daily_df.columns}")
        st.write(f"index  : {daily_df.index}")
    debug=False

    #st.stop()


    #return df
    returns_df=daily_df.copy().xs('Return%',axis=1,level=1)
    returns_df=returns_df.reset_index()

    returns_df['Datetime']=returns_df['Datetime'].apply(lambda x:x.split('-')[1])
    returns_df.rename(columns={'Datetime':'Time'},inplace=True)
    returns_df=returns_df.round(2)
    returns_df=returns_df.melt(
        id_vars='Time',
        var_name='Ticker',
        value_name='Returns%'
    )
    if debug:st.dataframe(returns_df)


    #get market value and total value
    value_df=daily_df.copy().loc[:,pd.IndexSlice[:,['MarketValue','Investment','Return%']]]
    value_df=value_df.reset_index()
    value_df['Datetime']=value_df['Datetime'].apply(lambda x:x.split('-')[1])
    value_df=value_df.round(2)

    #change the column names
    value_df.columns=[f'{a}_{b}'for a,b in value_df.columns]
    value_df.rename(columns={'Datetime_':'Time'},inplace=True)


    if debug:st.dataframe(value_df)
    if debug:print(value_df.columns)

    return_fig = px.line(returns_df, x='Time', y='Returns%', color='Ticker',
              title=f'Returns% Over a day on {date_radio}')

    # Add vertical lines
    return_fig.add_vline(x='12:00', line_width=2, line_dash="dash", line_color="red")
    return_fig.add_vline(x='14:00', line_width=2, line_dash="dash", line_color="red")

    return_fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Returns%',
        template='plotly_white',
        title={'x':0.5,'xanchor':'center'},
        height=500

    )
        

    st.plotly_chart(return_fig)


    df=value_df.copy()

    

    #debug 
    # st.write("Total_MarketValue min:", value_df['Total_MarketValue'].min())
    # st.write("Total_MarketValue <= 0 exists?:", (df['Total_MarketValue'] <= 0).any())
    # st.write("Total_MarketValue dtype:", df['Total_MarketValue'].dtype)

    tickers=['Total']+tickers

    if debug:st.write(f"tickers: {tickers}")
    inv_fig = make_subplots(
    rows=len(tickers), cols=1,
    shared_xaxes=False,
    subplot_titles=[f"{ticker}| changes on {date_radio} | Total Investment: {df[f'{ticker}_Investment'][0]:,}" for ticker in tickers],
    specs=[[{"type": "xy"}]]*len(tickers)) 

    # Plot each ticker's investment and market value
    for i, ticker in enumerate(tickers):
        investment_col = f"{ticker}_Investment"
        market_value_col = f"{ticker}_MarketValue"

        # Market Value line
        inv_fig.add_trace(go.Bar(
            x=df['Time'], y=df[market_value_col],
            name=f'{ticker} Market Value',
            showlegend=True #(i == 0)
        ), row=i + 1, col=1)

       
    # Update layout
    inv_fig.update_layout(
        #title=f'Market Value fluctation for {ticker} on {date_radio}',
        xaxis_title='Time',
        yaxis_title='Value [$]',
        #legend_title='Legend',
        #yaxis_type='log',
        template='plotly_white',
        height=500*len(tickers)
    )
    #Apply log scale to all y-axes
    log_y=True
    if log_y:
        for i in range(1, len(tickers) + 1):
            inv_fig.update_yaxes(type='log', row=i, col=1,tickformat=',',title_text='Market Value [$]')
            inv_fig.update_xaxes(row=i, col=1,title_text=f'[{date_radio}]')



    st.plotly_chart(inv_fig,use_container_width=True)

##check if the given date is business day or not
def is_business_day(date):
  '''
  This function checks if the given date is a business day or not
  '''
  return pd.to_datetime(date).weekday()<5

with tab3:
    #download yahoo data 

    #user input ticker, start_date, end_date,volume_threshold%,%change on the end date,holding period
    debug=False
    #ask the user for the ticker
    #user_ticker=st.text_input("Enter a ticker",value='TSLA',key='ticker').upper()

    #if debug:st.write(f'ticker: {user_ticker}')

    #start and end date
    start_date=st.date_input('Select start business date',value=pd.to_datetime("2025/01/02"))
    if debug:st.write(f'start_date: {start_date}')

    #check if the start date is a business day
    if not is_business_day(start_date):
       st.warning('Start date needs to be a valid business day !',icon='⚠️')
       st.stop()



    #last_business_day
    date_today=pd.to_datetime('today').normalize().date()
    if debug:st.write(f'today: {date_today}')
    bdate=pd.bdate_range(end=date_today,periods=1)[0]
    if debug:st.write(f'last_business_day: {bdate}')
    end_date=st.date_input('Select end business date',value=bdate)
    if debug:st.write(f'end_date: {end_date}')

    if not is_business_day(end_date):
        st.warning('End date needs to be a valid business day !',icon='⚠️')
        st.stop()

    #yfinance is exclusive for end date so making it inclusive
    temp_end_date=pd.to_datetime(end_date)+pd.Timedelta(days=1)

    if debug:st.write(f'temp_end_date: {temp_end_date}')
    #assert that end date is later than the start date
    if end_date<start_date:
        st.warning('End date needs to be later than Start date !',icon='⚠️')
        st.stop()

    #downloading the stock values between start and end date 
    try:
        df_temp=yf.download(org_tickers,start=start_date,end=temp_end_date,group_by='ticker')
    except:
        st.warning('Error occured try again with valid ticker !',icon='⚠️')
        st.stop()

    if df_temp.empty:
        st.warning('Error occured try again with a valid ticker !',icon='⚠️')
        st.stop()


# #reset to keep the date as the column
# #might need to change this part for the remote

    if debug:st.write(f'before resetting index ...{df_temp.columns}')

    if debug:st.write(df_temp)
    if debug:st.write(df_temp.columns)
    
# remote=True
# if remote:
#    df=df_temp[user_ticker]
# else:
#    df=df_temp.copy()


#date is changed here

    # df_temp=df_temp.reset_index(drop=False)
    # #df_temp=df_temp.reset_index(drop=False)
    # ##changing Date into Datetime
    # #df_temp['Date']=pd.to_datetime(df_temp['Date']) #in remote
    # df_temp['Date']=pd.to_datetime(df_temp['Date']) #in remote
    if debug:st.write(f'after resetting index df columns...{df_temp.columns}')

# #might need to change this part for the remote
# #remote=False
# #if remote:
# #   df=df_temp[user_ticker]
# #else:
# #   df=df_temp.copy()



#     #daily df
#     #daily_df=data[data.index.normalize()==date_radio]
#     daily_df=data[data.index.date==date_radio]

#     daily_df.index=daily_df.index.strftime("%m/%d-%H:%M")
#     if debug:st.dataframe(daily_df)

    for ticker in df_temp.columns.levels[0]:
        #st.write(f"data frame for {ticker}")
        #ticker_df=data[ticker]
        ticker_df=df_temp[ticker]
        #include the number of shares
        if debug:st.write(f"{ticker} df ..")
        if debug:st.dataframe(ticker_df)
        #dates
        portfolio_ticker_info=df_group[df_group['Ticker']==ticker]
        if debug:st.write(f"portfolio ticker info:\n{portfolio_ticker_info}")
        if debug:st.dataframe(portfolio_ticker_info)

        portfolio_ticker_num=portfolio_ticker_info['Shares'].values
        portfolio_ticker_investement=portfolio_ticker_info['TotalCost'].values[0]
    

        df_temp[(ticker,'TotalShares')]=[portfolio_ticker_num]*len(df_temp)#portfolio_ticker_info['Shares'].values*ticker_df['Close']
        df_temp[(ticker,'Investment')]=portfolio_ticker_investement#*len(daily_df)#portfolio_ticker_info['Shares'].values*ticker_df['Close']
        df_temp[(ticker,'MarketValue')]=portfolio_ticker_info['Shares'].values*ticker_df['Close']
        df_temp[(ticker,'Volume')]= round(df_temp[(ticker,'Volume')]/1e6,3)#volume into million

        #find the returns
        df_temp[(ticker,'Return%')]=100*df_temp[ticker]['Close'].pct_change()

    
    df_temp=df_temp.sort_index(axis=1)
    if debug:st.write(f"index and column names:\n{df_temp.columns}\n{df_temp.index}")
    if debug:st.dataframe(df_temp)

        #get the investment and total column
    market_value=df_temp.xs('MarketValue',axis=1,level=1)
    total_invest=df_temp.xs('Investment',axis=1,level=1)
        #st.dataframe(market_value)
        #st.dataframe(total_invest)

        #add total market value and total invesetment
    df_temp[('Total','MarketValue')]=market_value.sum(axis=1)
    df_temp[('Total','Investment')]=total_invest.sum(axis=1)

    if debug:st.dataframe(df_temp)


        #return df
    returns_df=df_temp.copy().xs('Return%',axis=1,level=1)
    returns_df=returns_df.reset_index()

        #returns_df['Datetime']=returns_df['Datetime'].apply(lambda x:x.split('-')[1])
        #returns_df.rename(columns={'Datetime':'Time'},inplace=True)
    returns_df=returns_df.round(2)
    returns_df=returns_df.melt(
            id_vars='Date',
            var_name='Ticker',
            value_name='Returns%'
        )
    if debug:st.dataframe(returns_df)


        #get market value and total value
    value_df=df_temp.copy().loc[:,pd.IndexSlice[:,['MarketValue','Investment','Return%']]]
    value_df=value_df.reset_index()
    #value_df['Datetime']=value_df['Datetime'].apply(lambda x:x.split('-')[1])
    value_df=value_df.round(2)

    #change the column names
    value_df.columns=[f'{a}_{b}'for a,b in value_df.columns]
    value_df.rename(columns={'Date_':'Date'},inplace=True)


    if debug:st.dataframe(value_df)
    if debug:print(value_df.columns)

    return_fig = px.line(returns_df, x='Date', y='Returns%', color='Ticker',
              title=f'Returns% Over {start_date.strftime("%Y-%m-%d")}---{end_date.strftime("%Y-%m-%d")}')

    # Add vertical lines
    # return_fig.add_vline(x='12:00', line_width=2, line_dash="dash", line_color="red")
    # return_fig.add_vline(x='14:00', line_width=2, line_dash="dash", line_color="red")

    return_fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Returns%',
        template='plotly_white',
        title={'x':0.5,'xanchor':'center'},
        height=500

    )
        

    st.plotly_chart(return_fig)


    df=value_df.copy()

    

    #debug 
    # st.write("Total_MarketValue min:", value_df['Total_MarketValue'].min())
    # st.write("Total_MarketValue <= 0 exists?:", (df['Total_MarketValue'] <= 0).any())
    # st.write("Total_MarketValue dtype:", df['Total_MarketValue'].dtype)

    tickers=['Total']+org_tickers

    if debug:st.write(f"tickers: {tickers}")
    inv_fig = make_subplots(
    rows=len(tickers), cols=1,
    shared_xaxes=False,
    subplot_titles=[f"{start_date.strftime('%Y-%m-%d')} === {end_date.strftime('%Y-%m-%d')} | {ticker.upper()} | Investment: {df[f'{ticker}_Investment'][0]:,}" for ticker in tickers],
    specs=[[{"type": "xy"}]]*len(tickers)) 

    # Plot each ticker's investment and market value
    for i, ticker in enumerate(tickers):
        investment_col = f"{ticker}_Investment"
        market_value_col = f"{ticker}_MarketValue"

        # Market Value line
        inv_fig.add_trace(go.Bar(
            x=df['Date'], y=df[market_value_col],
            name=f'{ticker} Market Value',
            showlegend=True #(i == 0)
        ), row=i + 1, col=1)

       
    # Update layout
    inv_fig.update_layout(
        #title=f'Market Value fluctation for {ticker} on {date_radio}',
        xaxis_title='Date',
        yaxis_title='Value [$]',
        #legend_title='Legend',
        #yaxis_type='log',
        template='plotly_white',
        height=500*len(tickers)
    )
    #Apply log scale to all y-axes
    holiday_list=[
 '2023-01-02',  # New Year's Day (observed)
 '2023-01-16',  # Martin Luther King Jr. Day
 '2023-02-20',  # Presidents' Day
 '2023-04-07',  # Good Friday
 '2023-05-29',  # Memorial Day
 '2023-06-19',  # Juneteenth National Independence Day
 '2023-07-04',  # Independence Day
 '2023-09-04',  # Labor Day
 '2023-11-23',  # Thanksgiving Day
 '2023-12-25',  # Christmas Day
 '2024-01-01',  # New Year's Day
 '2024-01-15',  # Martin Luther King Jr. Day
 '2024-02-19',  # Presidents' Day
 '2024-03-29',  # Good Friday
 '2024-05-27',  # Memorial Day
 '2024-06-19',  # Juneteenth National Independence Day
 '2024-07-04',  # Independence Day
 '2024-09-02',  # Labor Day
 '2024-11-28',  # Thanksgiving Day
 '2024-12-25',  # Christmas Day
 '2025-01-01',  # New Year's Day
 '2025-01-09',
 '2025-01-20',  # Martin Luther King Jr. Day
 '2025-02-17',  # Presidents' Day
 '2025-04-18',  # Good Friday
 '2025-05-26',  # Memorial Day
 '2025-06-19',  # Juneteenth National Independence Day
 '2025-07-04',  # Independence Day
 '2025-09-01',  # Labor Day
 '2025-11-27',  # Thanksgiving Day
 '2025-12-25'   # Christmas Day
]

    log_y=True
    if log_y:
        for i in range(1, len(tickers) + 1):
            inv_fig.update_yaxes(type='log', row=i, col=1,tickformat=',',title_text='Market Value [$]')
            inv_fig.update_xaxes(row=i, col=1,title_text='Date',rangebreaks=[dict(bounds=["sat","mon"]),dict(values=holiday_list)])



    st.plotly_chart(inv_fig,use_container_width=True)
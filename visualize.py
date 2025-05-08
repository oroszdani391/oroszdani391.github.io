import pandas as pd
import altair as alt
import os

try:
    # Read CSV file with semicolon separator and correct encoding
    df = pd.read_csv('data.csv', sep=';', encoding='latin1')
    
    # Print data info for debugging
    print("Data columns:", df.columns.tolist())
    print("\nSample data:")
    print(df[['Top speed (km/h)', 'Acceleration (s)']].head())
    
    # Clean the data
    # Convert string columns to numeric
    for col in ['Base price', 'Acceleration (s)']:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')
    
    # Convert numeric columns
    for col in ['Power (HP)', 'Top speed (km/h)', 'Displacement (ccm)']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Print cleaned data info
    print("\nCleaned data sample:")
    print(df[['Top speed (km/h)', 'Acceleration (s)']].head())
    print("\nData types:")
    print(df[['Top speed (km/h)', 'Acceleration (s)']].dtypes)
    print("\nNon-null counts:")
    print(df[['Top speed (km/h)', 'Acceleration (s)']].count())
    
    # Convert Generation to string and handle NaN
    df['Generation'] = df['Generation'].fillna('Unknown').astype(str)
    
    # Get unique generations and sort them, add 'Összes' (All) as the first option, remove 'Unknown'
    generations = sorted([g for g in df['Generation'].unique().tolist() if g != 'Unknown'])
    generations = ['Összes'] + generations
    
    # Create separate generation selections for each chart
    generation_selection1 = alt.selection_point(
        fields=['Generation'],
        bind=alt.binding_select(options=generations, name='Generáció:'),
        name='Select1',
        value='Összes'
    )
    generation_selection2 = alt.selection_point(
        fields=['Generation'],
        bind=alt.binding_select(options=generations, name='Generáció:'),
        name='Select2',
        value='Összes'
    )
    generation_selection3 = alt.selection_point(
        fields=['Generation'],
        bind=alt.binding_select(options=generations, name='Generáció:'),
        name='Select3',
        value='Összes'
    )
    
    # Set up axis and view config for all charts (white background for chart area, black text)
    axis_config = dict(
        grid=False,
        labelColor='#000',
        titleColor='#000',
        tickColor='#000',
        domainColor='#000'
    )
    view_config = dict(
        strokeWidth=0,
        fill='#fff'
    )

    # Create first visualization (Price vs Power)
    chart1 = alt.Chart(df).mark_circle(size=100).encode(
        x=alt.X('Power (HP):Q', title='Teljesítmény (LE)'),
        y=alt.Y('Base price:Q', title='Alapár (€)'),
        color=alt.condition(
            generation_selection1,
            alt.Color('Generation:N', scale=alt.Scale(scheme='category20')),
            alt.value('lightgray')
        ),
        tooltip=['Full car name', 'Power (HP)', 'Base price', 'Generation']
    ).add_params(
        generation_selection1
    ).transform_filter(
        "(isValid(Select1.Generation) ? (Select1.Generation == 'Összes' || datum.Generation == Select1.Generation) : true)"
    ).properties(
        width='container',
        height=500,
        title='BMW Adatok Vizualizációja - Ár és Teljesítmény'
    )
    
    # Create second visualization (Top Speed vs Acceleration)
    chart2 = alt.Chart(df).mark_circle(size=100).encode(
        x=alt.X('Acceleration (s):Q', title='Gyorsulás (0-100 km/h, s)'),
        y=alt.Y('Top speed (km/h):Q', title='Végsebesség (km/h)'),
        color=alt.condition(
            generation_selection2,
            alt.Color('Generation:N', scale=alt.Scale(scheme='category20')),
            alt.value('lightgray')
        ),
        tooltip=['Full car name', 'Top speed (km/h)', 'Acceleration (s)', 'Generation']
    ).add_params(
        generation_selection2
    ).transform_filter(
        "(isValid(Select2.Generation) ? (Select2.Generation == 'Összes' || datum.Generation == Select2.Generation) : true)"
    ).properties(
        width='container',
        height=500,
        title='BMW Adatok Vizualizációja - Sebesség és Gyorsulás'
    )
    
    # New bar chart: Body type vs Number of doors
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Number of doors:O', title='Ajtók száma'),
        y=alt.Y('count():Q', title='Autók száma'),
        color=alt.Color('Body type:N', title='Karosszéria típus', scale=alt.Scale(scheme='category20')),
        tooltip=['Body type', 'Number of doors', 'count()']
    ).properties(
        width='container',
        height=400,
        title='Karosszéria típus és ajtók száma szerinti eloszlás'
    )
    
    # Hexbin heatmap for Displacement (ccm) vs Power (HP)
    disp_power_hex = alt.Chart(df).mark_rect().encode(
        x=alt.X('Displacement (ccm):Q', bin=alt.Bin(maxbins=40), title='Lökettérfogat (ccm)'),
        y=alt.Y('Power (HP):Q', bin=alt.Bin(maxbins=40), title='Teljesítmény (LE)'),
        color=alt.Color('count():Q', scale=alt.Scale(scheme='turbo'), legend=alt.Legend(title='Autók száma')),
        tooltip=['count()']
    ).properties(
        width='container',
        height=500,
        title='Lökettérfogat és Teljesítmény - Sűrűségtérkép'
    )
    
    # Histogram: Curb weight (kg) by Model, with generation selection
    curb_weight_hist = alt.Chart(df).mark_bar().encode(
        x=alt.X('Curb weight (kg):Q', bin=alt.Bin(maxbins=40), title='Saját tömeg (kg)'),
        y=alt.Y('count():Q', title='Autók száma'),
        color=alt.Color('Model series:N', title='Modell', scale=alt.Scale(scheme='category20')),
        tooltip=['Model series', 'count()']
    ).add_params(
        generation_selection3
    ).transform_filter(
        "(isValid(Select3.Generation) ? (Select3.Generation == 'Összes' || datum.Generation == Select3.Generation) : true)"
    ).properties(
        width='container',
        height=400,
        title='Saját tömeg (kg) eloszlása modellek szerint'
    )
    
    # Save each chart with dropdown as its own HTML file, with .interactive() for zoom/pan
    chart1.interactive().save('chart1.html')
    chart2.interactive().save('chart2.html')
    bar_chart.interactive().save('bar_chart.html')
    disp_power_hex.interactive().save('disp_power_hex.html')
    curb_weight_hist.interactive().save('curb_weight_hist.html')

    # Main HTML wrapper with tabs for each chart, set iframe background to white
    main_html = '''
    <html>
    <head>
        <meta charset="utf-8">
        <title>BMW Adatvizualizáció</title>
        <style>
            body {
                background: #1a365d;
                margin: 0;
                padding: 0;
            }
            .bmw-logo {
                width: 150px;
                height: 150px;
                display: block;
                margin: 10px -50px -50px 10px;
            }
            .site-title {
                color: #fff;
                font-size: 3.5rem;
                font-weight: bold;
                text-align: center;
                margin-top: 10 px;
                margin-bottom: 30px;
                letter-spacing: 2px;
                text-shadow: 0 4px 24px #000, 0 1px 0 #4a90e2;
            }
            .tab-bar {
                display: flex;
                justify-content: center;
                margin-bottom: 30px;
            }
            .tab {
                background: #274472;
                color: #fff;
                border: none;
                outline: none;
                padding: 16px 32px;
                font-size: 1.2rem;
                cursor: pointer;
                margin: 0 4px;
                border-radius: 8px 8px 0 0;
                transition: background 0.2s;
            }
            .tab.active {
                background: #4a90e2;
                color: #fff;
                font-weight: bold;
            }
            .tab-content {
                display: none;
                width: auto;
                max-width: 1000px;
                margin: 40px auto;
                background: #fff;
                border-radius: 0 0 12px 12px;
                box-shadow: 0 2px 16px #0004;
                padding: 0;
            }
            .tab-content.active {
                display: block;
            }
            .chart-container {
                width: 100%;
                max-width: 1000px;
                min-width: 0;
                height: 650px;
                background: #fff;
                margin: 0 auto;
                border-radius: 0 0 12px 12px;
                box-shadow: 0 2px 16px #0004;
                padding: 0;
                display: flex;
                align-items: flex-start;
                justify-content: center;
            }
            .chart-container iframe {
                width: 100%;
                max-width: 1000px;
                min-width: 0;
                height: 650px;
                border: none;
                background: #fff;
                display: block;
            }
            .credit {
                position: fixed;
                left: 20px;
                bottom: 20px;
                color: #fff;
                font-size: 1.1rem;
                background: rgba(0,0,0,0.3);
                padding: 6px 16px;
                border-radius: 8px;
                z-index: 1000;
                font-family: Arial, sans-serif;
            }
            @media (max-width: 1200px) {
                .tab-content {
                    width: 100vw;
                    min-width: 0;
                }
                .chart-container {
                    width: 100vw;
                    min-width: 0;
                    max-width: 100vw;
                }
                .chart-container iframe {
                    width: 100vw;
                    min-width: 0;
                    max-width: 100vw;
                }
            }
            .tab-content-flex-row {
                display: flex;
                flex-direction: row;
                align-items: flex-start;
                justify-content: flex-start;
                max-width: 1000px;
                margin: 0 auto;
                width: 100%;
                background: #1a365d;
            }
            .desc-above-info {
                width: 320px;
                margin-left: 40px;
                background: #223a5e;
                color: #fff;
                font-size: 1.15rem;
                font-family: Arial, sans-serif;
                border-radius: 12px;
                padding: 22px 32px 16px 32px;
                box-shadow: 0 2px 16px #0002;
                line-height: 1.6;
            }
            .desc-side-info {
                width: 320px;
                margin-left: 40px;
                background: #223a5e;
                color: #fff;
                font-size: 1.15rem;
                font-family: Arial, sans-serif;
                border-radius: 12px;
                padding: 22px 32px 16px 32px;
                box-shadow: 0 2px 16px #0002;
                line-height: 1.6;
            }
        </style>
        <script>
            function showTab(idx) {
                var tabs = document.getElementsByClassName('tab');
                var contents = document.getElementsByClassName('tab-content');
                for (var i = 0; i < tabs.length; i++) {
                    tabs[i].classList.remove('active');
                    contents[i].classList.remove('active');
                }
                tabs[idx].classList.add('active');
                contents[idx].classList.add('active');
            }
            window.onload = function() { showTab(0); };
        </script>
    </head>
    <body>
        <img src="BMW.svg.png" class="bmw-logo" alt="BMW logo" />
        <div class="site-title">BMW Adatvizualizáció</div>
        <div class="tab-bar">
            <button class="tab" onclick="showTab(0)">Ár és Teljesítmény</button>
            <button class="tab" onclick="showTab(1)">Sebesség és Gyorsulás</button>
            <button class="tab" onclick="showTab(2)">Karosszéria és Ajtók</button>
            <button class="tab" onclick="showTab(3)">Lökettérfogat és Teljesítmény</button>
            <button class="tab" onclick="showTab(4)">Saját tömeg eloszlás</button>
        </div>
        <div class="tab-content"><div class="chart-container"><iframe src="chart1.html"></iframe></div></div>
        <div class="tab-content"><div class="chart-container"><iframe src="chart2.html"></iframe></div></div>
        <div class="tab-content"><div class="chart-container"><iframe src="bar_chart.html"></iframe></div></div>
        <div class="tab-content"><div class="chart-container"><iframe src="disp_power_hex.html"></iframe></div></div>
        <div class="tab-content"><div class="chart-container"><iframe src="curb_weight_hist.html"></iframe></div></div>
        <div class="credit">Credit: Orosz Daniel and Szabó Kevin</div>
    </body>
    </html>
    '''
    with open('visualization.html', 'w', encoding='utf-8') as f:
        f.write(main_html)
    print("\nAll charts exported. Open visualization.html to view them in tabs, each with its own dropdown and visible axes.")

    # Make charts interactive
    chart1 = chart1.interactive()
    chart2 = chart2.interactive()
    bar_chart = bar_chart.interactive()
    disp_power_hex = disp_power_hex.interactive()
    curb_weight_hist = curb_weight_hist.interactive()

except Exception as e:
    print(f"Error: {str(e)}")


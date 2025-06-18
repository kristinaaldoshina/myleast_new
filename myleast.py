import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# <>>>--- PAGE SETTINGS ---<<<>

st.set_page_config(layout="wide", page_title="Learning styles", page_icon="icon.ico")

# <>>>--- TABS ---<<<>

tab1, tab2, tab3, tab4 = st.tabs(["Home", "About", "HM test", "VAK test"])

# <>>>--- tab1 - HOME ---<<<>

with tab1:
    st.image("all.png", width=600)
    with open("home.html", 'r', encoding='utf-8') as f:
        home_content_1 = f.read()
    st.markdown(home_content_1, unsafe_allow_html=True)

    st.divider()

    with open("authors.html", 'r', encoding='utf-8') as f:
        home_content_2 = f.read()
    st.markdown(home_content_2, unsafe_allow_html=True)

    

# <>>>--- tab2 - ABOUT ---<<<>

with tab2:
    with open("about.html", 'r', encoding='utf-8') as f:
        lines = []
        for line in f:
            if line.strip() == '*':
                break
            lines.append(line)
        about_content_1 = "".join(lines)
    st.markdown(f"""<div style='text-align: right; font-style: italic;'>{about_content_1}</div>""", unsafe_allow_html=True)

    with open("about.html", 'r', encoding='utf-8') as f:
        collecting = False
        lines = []

        for line in f:
            stripped = line.strip()
            if stripped == '*':
                collecting = True
                continue
            elif stripped == '**':
                collecting = False
                break
            if collecting:
                lines.append(line)

        about_content_2 = "".join(lines)
    st.markdown(about_content_2, unsafe_allow_html=True)

    st.image("HM_cycle.png", width=400)

    with open("about.html", 'r', encoding='utf-8') as f:
        lines = []
        start_collecting = False

        for line in f:
            if not start_collecting:
                if line.strip() == '***':
                    start_collecting = True
                continue
            lines.append(line)

        about_content_3 = "".join(lines)
    st.markdown(about_content_3, unsafe_allow_html=True)

# <>>>--- tab3 - HM test ---<<<>

with tab3:
    if "hm_result_ready" not in st.session_state:
        st.session_state.hm_result_ready = False

    with open("hm_test.html", 'r', encoding='utf-8') as f:
        hm_test_content = f.read()
    st.markdown(hm_test_content, unsafe_allow_html=True)
    
    st.divider()

    hm_results = {"activist": 0,
                  "pragmatist": 0,
                  "reflector": 0,
                  "theorist": 0}

    hm_questions = pd.read_csv("hm_test.csv", delimiter=";")
    for idx, row in hm_questions.iterrows():
        hm_checkbox = st.checkbox(row["question"], key=f"checkbox_{row['number']}")
        if hm_checkbox:
            hm_results[row["type"]] += 1
    sorted_hm_results = dict(sorted(hm_results.items(), key=lambda x: x[1], reverse=True))

    if st.button('Show my result', key="generate_hm_test_result"):
        st.session_state.hm_result_ready = True

    if st.session_state.hm_result_ready == True:
        if sum(sorted_hm_results.values()) == 0:
                st.error("There is nothing to show yet. Please take the test")
        else:
            labels = list(sorted_hm_results.keys())
            values = list(sorted_hm_results.values())
            hm_colors = ['#4e5b1c', '#7c8736', '#9dae28', '#c2d33f']
            cumulative = [0] + [sum(values[:i]) for i in range(1, len(values))]
            fig, ax = plt.subplots(figsize=(8, 1.5))
            for i in range(len(values)):
                ax.barh("question 1", values[i], left=cumulative[i], color=hm_colors[i])
                if values[i] > 0:
                    ax.text(cumulative[i] + values[i]/2, 0, labels[i].title(), va='center', ha='center', color='white')
            
            ax.set_xlim(0, sum(values))
            ax.axis('off')
            st.pyplot(fig)
            
            st.divider()
            st.markdown("__Descriptions__")

            hm_file_map = {"activist": "activist.html",
                    "pragmatist": "pragmatist.html",
                    "theorist": "theorist.html",
                    "reflector": "reflector.html"}
            
            combined_descriptions = ""
            
            for type in sorted_hm_results:
                if sorted_hm_results[type] > 0:
                    with open(hm_file_map[type], 'r', encoding='utf-8') as f:
                        md_content = f.read()
                        combined_descriptions += f"<h3>{type.title()}</h3><br>\n{md_content}<hr>\n"
                        with st.expander(type.title()):
                            st.image(f"{type}.png", width=250)
                            st.markdown(md_content, unsafe_allow_html=True)
            
            st.download_button(
            label="Download descriptions",
            data=combined_descriptions,
            file_name="hm_descriptions.html",
            mime="text/html")


# <>>>--- tab4 - VAK test ---<<<>

with tab4:
    if "vak_result_ready" not in st.session_state:
            st.session_state.vak_result_ready = False

    with open("vak_test.html", 'r', encoding='utf-8') as f:
        vak_test_content = f.read()
    st.markdown(vak_test_content, unsafe_allow_html=True)
    
    st.divider()

    vak_results = {"auditory": 0, "kinestetic": 0, "visual": 0}
    sorted_vak_results = vak_results

    vak_questions = pd.read_csv("vak_test.csv", delimiter=";")
    
    for idx, row in vak_questions.iterrows():
        st.write(f"{row['number']}. {row["question"]}")

        v_key = f"v_{row['number']}"
        a_key = f"a_{row['number']}"
        k_key = f"k_{row['number']}"

        v = st.checkbox(row["visual"], key=v_key)
        a = st.checkbox(row["auditory"], key=a_key)
        k = st.checkbox(row["kinestetic"], key=k_key)

        if v and not (a or k):
            vak_results["visual"] += 1
        elif a and not (v or k):
            vak_results["auditory"] += 1
        elif k and not (v or a):
            vak_results["kinestetic"] += 1
        elif any([(v and k), (v and a), (k and a)]):
            st.warning("Please select only one option")

    sorted_vak_results = dict(sorted(vak_results.items(), key=lambda x: x[1], reverse=True))

    if st.button('Show my result', key="generate_vak_test_result"):
        st.session_state.vak_result_ready = True

    if st.session_state.vak_result_ready == True:
        if sum(sorted_vak_results.values()) == 0:
                st.error("There is nothing to show yet. Please take the test")
        else:
            labels = list(sorted_vak_results.keys())
            values = list(sorted_vak_results.values())
            vak_colors=['#4e5b1c', '#7c8736', '#9dae28']
            cumulative = [0] + [sum(values[:i]) for i in range(1, len(values))]
            fig, ax = plt.subplots(figsize=(8, 1.5))
            for i in range(len(values)):
                ax.barh("question 1", values[i], left=cumulative[i], color=vak_colors[i])
                if values[i] > 0:
                    ax.text(cumulative[i] + values[i]/2, 0, labels[i].title(), va='center', ha='center', color='white')
            ax.set_xlim(0, sum(values))
            ax.axis('off')
            st.pyplot(fig)
            
            st.divider()
            st.markdown("__Descriptions__")

            vak_file_map = {"visual": "visual.html", 
                        "auditory": "auditory.html", 
                        "kinestetic": "kinestetic.html"}
            
            combined_descriptions = ""
            
            for type in sorted_vak_results:
                if sorted_vak_results[type] > 0:
                    with open(vak_file_map[type], 'r', encoding='utf-8') as f:
                        md_content = f.read()
                        combined_descriptions += f"<h3>{type.title()}</h3><br>\n{md_content}<hr>\n"
                        with st.expander(type.title()):
                            st.image(f"{type}.png", width=200)
                            st.markdown(md_content, unsafe_allow_html=True)
    
            st.download_button(
            label="Download descriptions",
            data=combined_descriptions,
            file_name="vak_descriptions.html",
            mime="text/html")
                    
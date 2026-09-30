import datetime
import streamlit as st

# import re

# text = """set_page_config, sidebar, columns, divider,  tabs, expander, form, radio, selectbox, multiselect, text_input,
# checkbox, file_uploader, form_submit_button, title, caption, subheader, write, markdown, metric, dataframe,
# column_config.NumberColumn, bar_chart, progress, code, info, warning, success"""

# items = re.split(r',\s+', text.strip())
# print('\n'.join(items))

import re

path = "khj_streamlit_02.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 4~6번째 줄의 나열된 항목 부분만 정규식으로 찾아서 줄바꿈으로 치환
old_block = """set_page_config
sidebar
columns
divider
tabs
expander
form
radio
selectbox
multiselect
text_input
checkbox
file_uploader
form_submit_button
title
caption
subheader
write
markdown
metric
dataframe
column_config.NumberColumn
bar_chart
progress
code
info
warning
success"""

items = re.split(r',\s+', old_block.strip())
new_block = '\n'.join(items)

content = content.replace(old_block, new_block)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

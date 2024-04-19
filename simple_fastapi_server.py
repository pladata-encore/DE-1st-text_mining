from fastapi import FastAPI, Response
from io import BytesIO
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pymysql
import re
import os

# execution command
# uvicorn simple_fastapi_server:app --host 0.0.0.0 --port 8023 --reload

# get db_connection data from db_info.env
db_info = {}
with open("db_info.env", "r") as f:
  for line in f:
    key, value = line.strip().split("=")
    db_info[key] = value


def get_db_cur():
  # connect to db
  conn = pymysql.connect(
    host=db_info["DB_HOST"],
    user=db_info["DB_USER"],
    password=db_info["DB_PASS"],
    db=db_info["DB_NAME"],
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor  # Use DictCursor
  )
  cur = conn.cursor()
  return cur, conn

def close_db_cur(cur, conn):
  cur.close()
  conn.close()

# make fastAPI app instance
app = FastAPI()

# define routes "/"
@app.get("/")
async def root():
  """
  Return the first 10 rows of job_data table
  """
  cur, conn = get_db_cur()

  # execute sql
  sql = """
    SELECT *
    FROM job_data
    LIMIT 10
  """
  cur.execute(sql)
  result = cur.fetchall()
  close_db_cur(cur, conn)
  return result

# define routes "/jobs/req/{req}"
@app.get("/jobs/req/{req}")
async def read_jobs(req: int):
  """
  Return the jobs that require career >= req
  """
  cur, conn = get_db_cur()

  sql = """
    SELECT *
    FROM job_data jd
    WHERE jd.career >= %s;
  """ 
  cur.execute(sql, (req,))
  result = cur.fetchall()
  close_db_cur(cur, conn)
  return {"message": result}

# define routes "/jobs/skill/{skill}"
@app.get("/jobs/skill/{skill}")
async def read_skill(skill: str):
  """
  Return the jobs that require the skill
  """
  cur, conn = get_db_cur()

  sql = """
    SELECT *
    FROM job_data jd
    WHERE INSTR(tech_stack, %s) > 0;
  """ 
  cur.execute(sql, (skill,))
  result = cur.fetchall()
  total_count = len(result)
  close_db_cur(cur, conn)
  return {"count": total_count,"message": result}

# define routes "/jobs/date/{date}"
@app.get("/jobs/date/{date}")
async def read_date(date: str):
  """
  Return the jobs that are available after the date ex) 20240101 (yyyymmdd)
  """
  cur, conn = get_db_cur()
  if len(date) != 8:
    return {"message": "Invalid date format. Please use yyyymmdd format."}
  
  # transform date(yyyymmdd) to date(yyyy-mm-dd)
  date = date[:4] + "-" + date[4:6] + "-" + date[6:]
  # find jobs after the date
  sql = """
    SELECT *
    FROM job_data jd
    WHERE jd.date_until >= STR_TO_DATE(%s, '%%Y-%%m-%%d')
  """ 
  cur.execute(sql, (date,))
  result = cur.fetchall()
  close_db_cur(cur, conn)
  return {"message": result}

# define routes "/skill/wordcloud"
@app.get("/skill/wordcloud")
async def read_skill_wordcloud():
  """
  Return the wordcloud image of tech_stack
  """
  cur, conn = get_db_cur()

  word_count = Counter()
  sql = """
    SELECT tech_stack
    FROM job_data
  """
  cur.execute(sql)
  rows = cur.fetchall()
  for row in rows:
    # row = {'tech_stack': "Java, C++, Swift"}
    tech_stack = row['tech_stack']

    # extract words from tech_stack
    if tech_stack == None:
      continue
    else:
      # if item contain ' or " erase it
      tech_stack = re.sub(r'[\'\"]', '', tech_stack)
      words = tech_stack.split(',')
      for word in words:
        word_count[word] += 1

  # draw a word cloud
  wordcloud = WordCloud(width=1200, height=700, background_color='white').generate_from_frequencies(word_count)
  plt.figure(figsize=(20, 12))
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.axis('off')
  
  # return the image
  buf = BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  close_db_cur(cur, conn)
  return Response(content=buf.getvalue(), media_type="image/png")

# define routes "/requirement/wordcloud/{skill} default value as 'all'
@app.get("/requirement/wordcloud/{skill}")
async def read_requirement_wordcloud(skill: str):
  """
  Return the wordcloud image of requirement \n
      skill : str : skill name to filter the job data \n
      use "all" to get all data \n
  ex) \n
      /requirement/wordcloud/all \n
      /requirement/wordcloud/Java \n
  """
  cur, conn = get_db_cur()

  word_count = Counter()
  if skill == 'all':
    sql = """
      SELECT required
      FROM job_data
      LIMIT 200
    """
    cur.execute(sql)
  else:
    sql = """
      SELECT required
      FROM job_data a
      WHERE INSTR(a.tech_stack, %s) > 0
      LIMIT 200
    """
    cur.execute(sql, (skill,))
  rows = cur.fetchall()
  if len(rows) == 0:
    return {"message": "No data found"}
  for row in rows:
    # row = "very long korean text"
    req = row['required']
    if req == None:
      continue
    else:
      # erase special characters and emojis
      req = re.sub(r'[^\w\s]', '', req)
      # erase html tags
      req = re.sub(r'<.*?>', '', req)
      # erase numbers
      req = re.sub(r'\d', '', req)
      # erase specific html tag names and css attributes
      html_css_names = ['div', 'span', 'p', 'ul', 'li', 'classcolour', 'stylecolor', 'rgb', 'ol', 'a', 'strong', 'em', 'br', 'hr', 'img', 'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot', 'caption', 'col', 'colgroup']
      req = re.sub(r'|'.join(html_css_names), '', req)
      # erase some no-meaning korean
      no_mean_kor = ['분', '및', '수', '등', '있는', '있으신', '또는', '지급', '있습니다', '있어요', '년', '이후', '연', '만', '있게', '휴가',
      '따라', '전', '잘', '모든', '제공', '간식', '차', '각', '할', '선물', '출산', '취소될', '도서', '명절', '경조금', '안내', '시간', '이상', '협의',
      '드려요', '위해', '원', '시', '함께', '대한', '다양한', '필요한', '통해', '이상의', 'Ynj', '지원해', '위한', '지원', '있도록', '더', '등의', '변경될', '내',
      '상황에', '처우', '보유하신', '진행', '합격', '드립니다', '생일', '차면접', '가능', '관련된','식대', '복지', '후', '분을', '혹은', '전형', '가능하신', '중', '최종',
      '하는', '개월', '서류전형', '없는', '진행됩니다', '본', '자유로운', '따른', '원활한', '팀', '경우', '과제', '자유롭게', '지원합니다', '환경', '월', '보기', '채용',
      '연차', '근무', '이용한', '회사의', '있으며', '진행되며', '하고', '높은', '적합성']
      # only delete fully identical words (not partial or included words)
      req = re.sub(r'\b' + r'\b|\b'.join(no_mean_kor) + r'\b', '', req)
      # replace words
      replace_word = {'경험이':'경험', '경험을':'경험', '역량을':'역량', '이해를':'이해'}
      req = re.sub(r'\b' + r'\b|\b'.join(replace_word.keys()) + r'\b', lambda x: replace_word[x.group()], req)
      
      
      # extract words from required
      words = req.split()
      for word in words:
        word_count[word] += 1

  # draw a word cloud
  wordcloud = WordCloud(width=1200, height=700, font_path=os.getcwd() + '/GmarketSansTTFMedium.ttf', background_color='white').generate_from_frequencies(word_count)
  plt.figure(figsize=(20, 12))
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.axis('off')
  
  # return the image
  buf = BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  close_db_cur(cur, conn)
  return Response(content=buf.getvalue(), media_type="image/png")

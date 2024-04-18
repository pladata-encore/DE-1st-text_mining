from fastapi import FastAPI, Response
from io import BytesIO
import pymysql
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# execution command
# uvicorn simple_fastapi_server:app --host 0.0.0.0 --port 8023 --reload

# get db_connection data from db_info.env
db_info = {}
with open("db_info.env", "r") as f:
  for line in f:
    key, value = line.strip().split("=")
    db_info[key] = value

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

# make fastAPI app instance
app = FastAPI()

# define routes "/"
@app.get("/")
async def root():
  """
  Return the first 10 rows of job_data table
  """
  # execute sql
  sql = """
    SELECT *
    FROM job_data_t
    LIMIT 10
  """
  cur.execute(sql)
  result = cur.fetchall()
  return result

# define routes "/jobs/req/{req}"
@app.get("/jobs/req/{req}")
async def read_jobs(req: int):
  """
  Return the jobs that require career >= req
  """
  sql = """
    SELECT *
    FROM job_data jd_t
    WHERE jd.career >= %s;
  """ 
  cur.execute(sql, (req,))
  result = cur.fetchall()
  return {"message": result}

# define routes "/jobs/skill/{skill}"
@app.get("jobs/skill/{skill}")
async def read_skill(skill: str):
  """
  Return the jobs that require the skill
  """
  sql = """
    SELECT *
    FROM job_data jd_t
    WHERE INSTR(tech_stack, %s) > 0;
  """ 
  cur.execute(sql, (skill,))
  result = cur.fetchall()
  total_count = len(result)
  return {"count": total_count,"message": result}

# define routes "/jobs/date/{date}"
@app.get("/jobs/date/{date}")
async def read_date(date: str):
  """
  Return the jobs that are available after the date
  """
  if len(date) != 8:
    return {"message": "Invalid date format. Please use yyyymmdd format."}
  
  # transform date(yyyymmdd) to date(yyyy-mm-dd)
  date = date[:4] + "-" + date[4:6] + "-" + date[6:]
  # find jobs after the date
  sql = """
    SELECT *
    FROM job_data jd_t
    WHERE jd.date_until >= STR_TO_DATE(%s, '%%Y-%%m-%%d')
  """ 
  cur.execute(sql, (date,))
  result = cur.fetchall()
  return {"message": result}

# define routes "/skill/wordcloud"
@app.get("/skill/wordcloud")
async def read_wordcloud():
  """
  Return the wordcloud image of tech_stack
  """
  word_count = Counter()
  sql = """
    SELECT tech_stack
    FROM job_data_t
  """
  cur.execute(sql)
  rows = cur.fetchall()
  for row in rows:
    # row = {'tech_stack': "['Java', 'C++', 'Swift']"}
    tech_stack = row['tech_stack']
    # extract words from tech_stack
    words = re.findall(r"'(.*?)'", tech_stack)
    for word in words:
      word_count[word] += 1

  # draw a word cloud
  wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_count)
  plt.figure(figsize=(10, 6))
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.axis('off')
  
  # return the image
  buf = BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  return Response(content=buf.getvalue(), media_type="image/png")

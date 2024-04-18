from fastapi import FastAPI
import pymysql

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
    FROM job_data
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
    FROM job_data jd
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
    FROM job_data jd
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
    FROM job_data jd
    WHERE jd.date_until >= STR_TO_DATE(%s, '%%Y-%%m-%%d')
  """ 
  cur.execute(sql, (date,))
  result = cur.fetchall()
  return {"message": result}
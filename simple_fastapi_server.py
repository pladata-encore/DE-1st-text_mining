import uvicorn
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
  charset='utf8'
)
cur = conn.cursor()

# make fastAPI app instance
app = FastAPI()

# define routes "/"
@app.get("/")
async def root():
  # execute sql
  sql = "SELECT * FROM job_data LIMIT 5"
  cur.execute(sql)
  result = cur.fetchall()
  curaaaaaaaaaaaaaaaaaaaaa+a+
  con.close()
  conn.close()
  return {"message": result}

# define routes "/jobs"
@app.get("/jobs")
async def read_jobs():
  return {"jobs": [{"title": "job1"}, {"title": "job2"}]}

# define routes "/skills/{skill}"
@app.get("/skills/{skill}")
async def read_skill(skill: str):
  return {"skill": skill}
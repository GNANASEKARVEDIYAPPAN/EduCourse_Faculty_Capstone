import os, sqlite3, json, csv, io
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
app=Flask(__name__); app.secret_key=os.environ.get('SECRET_KEY','change-this-secret-before-deployment'); DB=os.path.join(os.path.dirname(__file__),'educourse.db')
PARTS=['Course Planning','Course Website','Experiential Learning','Interactive Learning Resource','Assessment Design','Continuous Assessment Automation','Outcome-Based Analysis','AI Agent for Course Management','Research Integration','Responsible AI Use']
def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 with conn() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password TEXT NOT NULL,role TEXT NOT NULL); CREATE TABLE IF NOT EXISTS subjects(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,code TEXT NOT NULL,name TEXT NOT NULL,department TEXT,semester TEXT,FOREIGN KEY(user_id) REFERENCES users(id)); CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,subject_id INTEGER NOT NULL,part INTEGER NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);''')
  if not c.execute('SELECT 1 FROM users').fetchone(): c.execute('INSERT INTO users(username,password,role) VALUES(?,?,?)',('faculty',generate_password_hash('Faculty@123'),'faculty'))
def login_required(f):
 @wraps(f)
 def wrapper(*a,**kw):
  if 'uid' not in session:return redirect(url_for('login'))
  return f(*a,**kw)
 return wrapper
def subjects():
 with conn() as c:return c.execute('SELECT * FROM subjects WHERE user_id=? ORDER BY id DESC',(session['uid'],)).fetchall()
@app.route('/',methods=['GET','POST'])
def login():
 if request.method=='POST':
  with conn() as c:u=c.execute('SELECT * FROM users WHERE username=?',(request.form.get('username',''),)).fetchone()
  if u and check_password_hash(u['password'],request.form.get('password','')):session.clear();session.update(uid=u['id'],username=u['username'],role=u['role']);return redirect(url_for('dashboard'))
  flash('Invalid username or password')
 return render_template('login.html')
@app.route('/logout')
def logout():session.clear();return redirect(url_for('login'))
@app.route('/dashboard')
@login_required
def dashboard():return render_template('dashboard.html',parts=PARTS,subjects=subjects())
@app.route('/subjects',methods=['POST'])
@login_required
def add_subject():
 with conn() as c:c.execute('INSERT INTO subjects(user_id,code,name,department,semester) VALUES(?,?,?,?,?)',(session['uid'],request.form['code'].strip(),request.form['name'].strip(),request.form.get('department',''),request.form.get('semester','')))
 return redirect(url_for('dashboard'))
@app.route('/part/<int:number>',methods=['GET','POST'])
@login_required
def part(number):
 if number not in range(1,11):return 'Not found',404
 ss=subjects();sid=request.values.get('subject_id',type=int) or (ss[0]['id'] if ss else None)
 if sid and not any(s['id']==sid for s in ss):return 'Forbidden',403
 if request.method=='POST':
  if not sid:flash('Create a subject first');return redirect(url_for('dashboard'))
  title=request.form.get('title','').strip();content=request.form.get('content','').strip()
  if title and content:
   with conn() as c:c.execute('INSERT INTO records(user_id,subject_id,part,title,content) VALUES(?,?,?,?,?)',(session['uid'],sid,number,title,content))
  return redirect(url_for('part',number=number,subject_id=sid))
 with conn() as c:rows=c.execute('SELECT * FROM records WHERE user_id=? AND subject_id=? AND part=? ORDER BY id DESC',(session['uid'],sid,number)).fetchall() if sid else []
 return render_template('part.html',parts=PARTS,number=number,subjects=ss,sid=sid,records=rows)
@app.route('/record/<int:rid>/delete',methods=['POST'])
@login_required
def delete(rid):
 with conn() as c:
  row=c.execute('SELECT part,subject_id FROM records WHERE id=? AND user_id=?',(rid,session['uid'])).fetchone()
  if row:c.execute('DELETE FROM records WHERE id=? AND user_id=?',(rid,session['uid']))
 return redirect(url_for('part',number=row['part'],subject_id=row['subject_id'])) if row else redirect(url_for('dashboard'))
@app.route('/export/<int:sid>')
@login_required
def export(sid):
 with conn() as c:
  s=c.execute('SELECT * FROM subjects WHERE id=? AND user_id=?',(sid,session['uid'])).fetchone()
  if not s:return 'Forbidden',403
  rows=c.execute('SELECT part,title,content,created_at FROM records WHERE subject_id=? AND user_id=?',(sid,session['uid'])).fetchall()
 return Response(json.dumps({'subject':dict(s),'records':[dict(r) for r in rows]},indent=2),mimetype='application/json',headers={'Content-Disposition':f'attachment; filename=course_{sid}.json'})
@app.route('/assistant',methods=['POST'])
@login_required
def assistant():
 sid=request.form.get('subject_id',type=int);q=request.form.get('question','').lower()
 with conn() as c:
  s=c.execute('SELECT * FROM subjects WHERE id=? AND user_id=?',(sid,session['uid'])).fetchone()
  if not s:return jsonify(answer='Select an authorized subject.'),403
  rows=c.execute('SELECT part,title,content FROM records WHERE subject_id=? AND user_id=?',(sid,session['uid'])).fetchall()
 matches=[r for r in rows if any(w in (r['title']+' '+r['content']).lower() for w in q.split() if len(w)>3)]
 return jsonify(answer='\n\n'.join(f"Part {r['part']} – {r['title']}: {r['content'][:450]}" for r in matches[:3]) or 'No matching saved course information. This is a local retrieval assistant, not a live generative AI service.')
if __name__=='__main__':init();app.run(debug=False)

from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key ="awoa"
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


@app.route("/")
def index():
    if 'login' not in session:
        return redirect(url_for('login'))
    list_mahasiswa = []
    docs = db.collection("mahasiswa").order_by("nilai", direction=firestore.Query.DESCENDING).stream()
    for doc in docs:
        # to_dict() mengubah object firebase ke dictionary/object python
        mhs = doc.to_dict()
        mhs["id"] = doc.id

        # append buat memasukkan mhs ke list_mahasiswa
        list_mahasiswa.append(mhs)
    # return jsonify(list_mhs)
    return render_template("dashboard.html", mhs = list_mahasiswa)

@app.route("/api/mhs/<user_id>")
def api_mhs(user_id):
        
    mhs = db.collection("mahasiswa").document(user_id).get().to_dict()
    mhs.pop("pas")
    return jsonify(mhs)
@app.route("/login", methods=["POST","GET"])
def login():
    pesan = ""
    if request.method == "POST":
        

        docs = db.collection("mahasiswa").stream()
        for doc in docs:    
            datamhs = doc.to_dict()
            if request.form['username'] == datamhs['nama']:
                if request.form['password'] == datamhs['pas']:
                    
                    session['login']= True
                    session["user"] = datamhs
                    
                    session["userid"] = doc.id
                    return redirect(url_for("index"))
                else:
                    pesan = "Pasword Salah!!"
                break    
            pesan = "Username Salah"
            
    return render_template("login.html", pesan = pesan)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/regis", methods=["POST", "GET"])
def regis():
    pesan = ""
    if request.method == "POST":
        docs = db.collection("mahasiswa").where("nama", "==", request.form["nama"]).stream()
        for doc in docs:
            pesan=" Maaf, Username telah terdaftar"
            return render_template("regis.html", pesan = pesan)
        data = {
            "nama": request.form["nama"],
            "nilai": int(request.form["nilai"]),
            "pas": request.form['password']
        }
        db.collection("mahasiswa").add(data)
        pesan = "Akun telah dibuat"
        return redirect(url_for('login'))
    return render_template("regis.html")


@app.route("/profil", methods=["POST","GET"])
def profil():
    if 'login' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        doc_ref = db.collection("mahasiswa").document(session['userid'])
        data = {
            "nama":request.form["nama"],
            "nilai":int(request.form["nilai"]),
            "pas":request.form["password"],
        }

        doc_ref.update(data)
        return render_template("profil.html", data1 = data)
    data = db.collection("mahasiswa").document(session['userid']).get().to_dict()
    return render_template("profil.html", data1 = data)
if__name__=='__main__'
    app.run(debug=True)
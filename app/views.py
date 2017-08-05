from flask import render_template, request, g, session, redirect, url_for
from app import app
import sqlite3
from Crypto.Hash import SHA
from utils import fromArrayToString,checkWinner

def deleta(pk):
    time.sleep(15)
    cur = g.db.cursor()
    cur.execute("DELETE FROM partidas WHERE idpartidas=?",(pk,))
    g.db.commit()

@app.route('/')
@app.route('/index')
def index():
    if "jogador" in session.keys():
        return redirect( url_for('salas'))
    return redirect(url_for('login'))
#    return render_template("Ganhou.html")

@app.route('/login', methods=['GET'])
def login():
    if "jogador" in session.keys():
        logout()
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():

    cur = g.db.cursor()
    cur.execute("SELECT * FROM jogador WHERE username=?;",(request.form['username'],))

    data = cur.fetchall()
    cur.close()

    test = SHA.new(request.form['senha'])

    if data != []:
        if data[0]['senha'] == test.hexdigest():
            session['jogador'] = data[0]['idjogador']
            return render_template("logado.html")
    return render_template("senhaerro.html")


@app.route('/cadastro', methods=['GET'])
def cadastro():
    if "jogador" in session.keys():
        logout()
    return render_template('cadastro.html')


@app.route('/cadastro', methods=['POST'])
def cadastro_post():
    if request.form['username'] != "":
        if request.form['senha'] != "" and request.form['senha'] == request.form['confsenha']:
            try:
                hash = SHA.new(request.form['senha'])
                sql = "INSERT INTO jogador (username,senha) VALUES (?,?)"

                cur = g.db.cursor()
                cur.execute(sql,(request.form['username'],hash.hexdigest()))
                g.db.commit()
                cur.close()
                return render_template('sucesso.html')
            except:
                pass
    return render_template('erro.html')

@app.route("/salas", methods=['GET'])
def salas():
    cur = g.db.cursor()
    cur.execute("SELECT p.idpartidas,u.username FROM partidas p, jogador u WHERE u.idjogador=p.jogador1;")
    data = cur.fetchall()
    cur.close()
    return render_template("salas.html", rows=data)

@app.route("/salas", methods=['POST'])
def salasP():
    if request.json == "criar":
        cur = g.db.cursor()
        cur.execute("INSERT INTO partidas (jogador1,jogadordavez) VALUES (?,?)", (session['jogador'],session['jogador']))
        g.db.commit()
        cur = g.db.cursor()
        cur.execute("SELECT p.idpartidas FROM partidas p WHERE p.jogador1=?;",(session['jogador'],))
        data = cur.fetchone()
        cur.close()
        return '/sala/'+str(data['idpartidas'])


@app.route("/logout")
def logout():
    try:
        cur = g.db.cursor()
        cur.execute("SELECT p.idpartidas FROM partidas p WHERE p.jogador1=?;",(session['jogador'],))
        data = cur.fetchall()
        cur.close()
        cur = g.db.cursor()
        for i in data:
            cur.execute("DELETE FROM partidas WHERE jogador1=? or jogador2=?",(session["jogador"],session["jogador"]))
        g.db.commit()
        del session["jogador"]
    except :
        pass

    return redirect(url_for('index'))

@app.route("/recordes")
def recordes():
    cur = g.db.cursor()
    cur.execute("SELECT username,pontuacao FROM jogador WHERE pontuacao>0 ORDER BY pontuacao DESC;")
    data = cur.fetchall()
    cur.close()
    return render_template("recordes.html", rows=data)

@app.route("/historico")
def historico():
    cur = g.db.cursor()
    cur.execute("SELECT * FROM historico")
    data = cur.fetchall()
    cur.close()
    return render_template("resultados.html", rows=data)

@app.route('/enter/<pk>')
def entrar(pk):
    cur = g.db.cursor()
    cur.execute('SELECT jogador1,jogador2 from partidas where idpartidas=?',(pk,))
    data = cur.fetchone();
    cur.close()
    if data['jogador2'] == None and data['jogador1'] != session['jogador']:
        cur = g.db.cursor()
        cur.execute("UPDATE partidas SET jogador2=? WHERE idpartidas=?",(session['jogador'],pk,))
        g.db.commit()
        return redirect('/sala/'+pk)
    else:
        return redirect('/sala/'+pk)

@app.route('/sala/<pk>', methods=['GET'])
def sala(pk):

    #try:
    cur = g.db.cursor()
    cur.execute('SELECT jogador2 from partidas where idpartidas=?',(pk,))
    data = cur.fetchone();
    cur.close()
    if data[0] != None:
        cur = g.db.cursor()
        cur.execute('SELECT tabuleiro from partidas where idpartidas=?',(pk,))
        data = cur.fetchone();
        cur.close()

        tabuleiro = data['tabuleiro'].split(',')

        tabu = {
            "pos0":tabuleiro[0],
            "pos1":tabuleiro[1],
            "pos2":tabuleiro[2],
            "pos3":tabuleiro[3],
            "pos4":tabuleiro[4],
            "pos5":tabuleiro[5],
            "pos6":tabuleiro[6],
            "pos7":tabuleiro[7],
            "pos8":tabuleiro[8]
        }

        if checkWinner(tabu)[0]:
            cur = g.db.cursor()
            cur.execute('SELECT jogador1,jogador2 from partidas where idpartidas=?',(pk,))
            data = cur.fetchone();
            cur.close()

            if checkWinner(tabu)[1] == "X":
                if session['jogador'] == data['jogador1']:
                    cur = g.db.cursor()
                    cur.execute("INSERT INTO historico (jogador1,jogador2,vencedor) VALUES (?,?,?)",(data['jogador1'],data['jogador2'],data['jogador1']))
                    cur.execute("UPDATE jogador SET pontuacao=pontuacao+1 where idjogador=?",(data['jogador1']))
                    deleta(pk)
                    g.db.commit()
                    return render_template("Ganhou.html")
                elif session['jogador'] == data['jogador2']:
                    return render_template("Perdeu.html")
                else:
                    return render_template('partidaEncerrada.html')


            if checkWinner(tabu)[1] == "O":
                if session['jogador'] == data['jogador1']:
                    return render_template("Perdeu.html")
                elif session['jogador'] == data['jogador2']:

                    cur = g.db.cursor()
                    cur.execute("UPDATE jogador SET pontuacao=pontuacao+1 where idjogador=?",(data['jogador2']))
                    cur.execute("INSERT INTO historico (jogador1,jogador2,vencedor) VALUES (?,?,?)",(data['jogador1'],data['jogador2'],data['jogador2']))
                    deleta(pk)
                    g.db.commit()
                    return render_template("Ganhou.html")
                else:
                    return render_template('partidaEncerrada.html')


            if checkWinner(tabu)[1] == 'velha':
                if session['jogador'] == data['jogador1']:
                    cur = g.db.cursor()
                    cur.execute("INSERT INTO historico (jogador1,jogador2,vencedor) VALUES (?,?,?)",(data['jogador1'],data['jogador2'],'velha'))
                    deleta(pk)
                    g.db.commit()

                return render_template("partidaEncerradaV.html")


        return render_template("tabuleiro.html", tabu=tabu)
    return render_template("aguarde.html")
    #except:
    #    return redirect('/historico')

@app.route('/sala/<pk>', methods=['POST'])
def salap(pk):
    var = request.json
    cur = g.db.cursor()
    cur.execute('SELECT jogador1, jogadordavez, tabuleiro from partidas where idpartidas=?',(pk,))
    data = cur.fetchone();
    if session['jogador'] == data['jogadordavez']:
        tabuleiro = data['tabuleiro'].split(',')
        if tabuleiro[int(request.json)] == "  ":
            if session['jogador'] == data['jogador1']:
                tabuleiro[int(request.json)] = "X"
                cur = g.db.cursor()
                cur.execute("UPDATE partidas SET jogadordavez=jogador2 WHERE idpartidas=?",(pk,))
            else:
                tabuleiro[int(request.json)] = "O"
                cur.execute("UPDATE partidas SET jogadordavez=jogador1 WHERE idpartidas=?",(pk,))
        tabustr = fromArrayToString(tabuleiro)

        cur = g.db.cursor()
        cur.execute("UPDATE partidas SET tabuleiro=? WHERE idpartidas=?",(tabustr,pk,))
        cur.close()
        g.db.commit()



        return sala(pk)



@app.route("/conta", methods=["GET"])
def conta():
    return render_template("conta.html")

@app.route("/conta", methods=["Post"])
def contap():
    cur = g.db.cursor()
    cur.execute("SELECT * From jogador Where idjogador=?",(session['jogador'],))
    data = cur.fetchall()
    cur.close()

    hash = SHA.new(request.form['senha'])

    if hash.hexdigest() == data[0]['senha']:
        if request.form['novasenha'] == request.form['confnovasenha']:
            hash2 = SHA.new(request.form['novasenha'])
            cur = g.db.cursor()
            cur.execute("UPDATE jogador SET senha=? WHERE idjogador=?", (hash2.hexdigest(),data[0]['idjogador']))
            cur.close()
            g.db.commit()

            return render_template("senhaAlterSucess.html")






@app.before_request
def before_request():
   g.db = sqlite3.connect("OLG.db")
   g.db.row_factory = sqlite3.Row

@app.teardown_request
def teardown_request(exception):
    g.db.close()

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'chave_super_secreta_padrao')

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///calorifit_v3.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configuração de E-mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.googlemail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'calorifit@noreply.com')
mail = Mail(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Float, nullable=False) # em kg
    altura = db.Column(db.Float, nullable=False) # em cm
    sexo = db.Column(db.String(1), nullable=False) # 'M' ou 'F'
    objetivo = db.Column(db.String(50), nullable=True)
    anotacoes = db.Column(db.Text, nullable=True)
    refeicoes = db.relationship('Refeicao', backref='user', lazy=True)
    exercicios = db.relationship('Exercicio', backref='user', lazy=True)
    aguas = db.relationship('Agua', backref='user', lazy=True)
    lembretes = db.relationship('Lembrete', backref='user', lazy=True)
    pesos = db.relationship('PesoLog', backref='user', lazy=True, order_by='PesoLog.data_crua')

    def get_reset_token(self):
        s = URLSafeTimedSerializer(app.secret_key)
        return s.dumps(self.email, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = URLSafeTimedSerializer(app.secret_key)
        try:
            email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
        except:
            return None
        return User.query.filter_by(email=email).first()

    def calcular_bmr(self):
        # Fórmula de Harris-Benedict
        if self.sexo.upper() == 'M':
            return 88.362 + (13.397 * self.peso) + (4.799 * self.altura) - (5.677 * self.idade)
        else:
            return 447.593 + (9.247 * self.peso) + (3.098 * self.altura) - (4.330 * self.idade)

    def calcular_meta_agua(self):
        if self.idade < 18:
            return int(self.peso * 40)
        elif 18 <= self.idade <= 55:
            return int(self.peso * 35)
        elif 55 < self.idade <= 65:
            return int(self.peso * 30)
        else:
            return int(self.peso * 25)

class Refeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Exercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Agua(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantidade_ml = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Lembrete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(200), nullable=False)
    concluido = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class PesoLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.String(50), nullable=False)
    data_crua = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Redefinição de Senha - CaloriFit',
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''Para redefinir sua senha, visite o seguinte link:
{url_for('reset_token', token=token, _external=True)}

Se você não solicitou esta alteração, ignore este e-mail.
'''
    mail.send(msg)

# Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, senha):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login inválido. Verifique suas credenciais.', 'error')
    return render_template('login.html')

@app.route('/login_visitante')
def login_visitante():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    email_visitante = "visitante@calorifit.com"
    user = User.query.filter_by(email=email_visitante).first()
    
    if not user:
        user = User(
            email=email_visitante,
            password_hash=generate_password_hash("senha_visitante_123"),
            nome="Visitante",
            idade=25,
            peso=75.0,
            altura=175.0,
            sexo="M",
            objetivo="Explorar o App",
            anotacoes="Esta é uma conta compartilhada para testes e demonstração."
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    flash('Bem-vindo! Você está acessando como Visitante. Lembre-se: seus dados são compartilhados.', 'info')
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        nome = request.form.get('nome')
        sexo = request.form.get('sexo')
        objetivo = request.form.get('objetivo')
        anotacoes = request.form.get('anotacoes')

        try:
            idade = int(request.form.get('idade', 0))
            peso = float(request.form.get('peso', 0))
            altura = float(request.form.get('altura', 0))
        except (ValueError, TypeError):
            flash('Por favor, insira valores numéricos válidos para idade, peso e altura.', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('register'))

        novo_usuario = User(
            email=email,
            password_hash=generate_password_hash(senha),
            nome=nome,
            idade=idade,
            peso=peso,
            altura=altura,
            sexo=sexo,
            objetivo=objetivo,
            anotacoes=anotacoes
        )
        db.session.add(novo_usuario)
        db.session.commit()
        login_user(novo_usuario)
        return redirect(url_for('home'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            try:
                send_reset_email(user)
                flash('Um e-mail foi enviado com instruções para redefinir sua senha.', 'info')
            except Exception as e:
                flash(f'Erro ao enviar e-mail: {str(e)}', 'error')
        else:
            flash('Não existe uma conta com este e-mail.', 'error')
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Esse é um token inválido ou expirado.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'error')
            return render_template('reset_password.html')
            
        user.password_hash = generate_password_hash(senha)
        db.session.commit()
        flash('Sua senha foi atualizada! Você já pode fazer login.', 'info')
        return redirect(url_for('login'))
        
    return render_template('reset_password.html')

# Dashboard
@app.route('/')
@login_required
def home():
    refeicoes_data = Refeicao.query.filter_by(user_id=current_user.id).all()
    exercicios_data = Exercicio.query.filter_by(user_id=current_user.id).all()
    aguas_data = Agua.query.filter_by(user_id=current_user.id).all()
    lembretes = Lembrete.query.filter_by(user_id=current_user.id).all()
    pesos_data = PesoLog.query.filter_by(user_id=current_user.id).order_by(PesoLog.data_crua.asc()).all()
    
    # Pegar data do calendário (ou hoje)
    data_selecionada_input = request.args.get('data') # formato YYYY-MM-DD do input date
    if data_selecionada_input:
        dt_obj = datetime.strptime(data_selecionada_input, '%Y-%m-%d')
        hj = dt_obj.strftime("%d/%m/%Y")
        data_exibicao = data_selecionada_input
    else:
        hj = datetime.now().strftime("%d/%m/%Y")
        data_exibicao = datetime.now().strftime("%Y-%m-%d")
    
    # Processamento para agrupar por dia (Gráficos melhorados)
    consumo_por_dia = {}
    gasto_por_dia = {}
    total_consumido = 0
    total_gasto = 0
    agua_consumida = 0
    
    for r in refeicoes_data:
        dia = r.data.split(' ')[0]
        consumo_por_dia[dia] = consumo_por_dia.get(dia, 0) + r.calorias
        if dia == hj:
            total_consumido += r.calorias
            
    for e in exercicios_data:
        dia = e.data.split(' ')[0]
        gasto_por_dia[dia] = gasto_por_dia.get(dia, 0) + e.calorias
        if dia == hj:
            total_gasto += e.calorias

    for a in aguas_data:
        dia = a.data.split(' ')[0]
        if dia == hj:
            agua_consumida += a.quantidade_ml

    # Combinar todas as datas (únicas e ordenadas cronologicamente)
    # Inclui datas de refeições, exercícios e água para garantir gráfico completo
    datas_refeicoes = [r.data.split(' ')[0] for r in refeicoes_data]
    datas_exercicios = [e.data.split(' ')[0] for e in exercicios_data]
    datas_aguas = [a.data.split(' ')[0] for a in aguas_data]
    
    todas_datas = sorted(
        list(set(datas_refeicoes + datas_exercicios + datas_aguas)),
        key=lambda x: datetime.strptime(x, "%d/%m/%Y")
    )
    
    grafico_consumo = [consumo_por_dia.get(d, 0) for d in todas_datas]
    grafico_gasto = [gasto_por_dia.get(d, 0) for d in todas_datas]
    
    # Harris-Benedict BMR
    bmr = current_user.calcular_bmr()
    calorias_restantes = bmr + total_gasto - total_consumido
    
    meta_agua = current_user.calcular_meta_agua()

    return render_template(
        'home.html',
        bmr=round(bmr, 2),
        total_consumido=total_consumido,
        total_gasto=total_gasto,
        calorias_restantes=round(calorias_restantes, 2),
        agua_consumida=agua_consumida,
        meta_agua=meta_agua,
        lembretes=lembretes,
        labels_dias=todas_datas,
        dados_consumo=grafico_consumo,
        dados_gasto=grafico_gasto,
        data_exibicao=data_exibicao,
        labels_peso=[p.data for p in pesos_data],
        valores_peso=[p.valor for p in pesos_data]
    )

@app.route('/add_peso', methods=['POST'])
@login_required
def add_peso():
    try:
        valor = float(request.form['valor'])
        data_log = request.form.get('data_log')
        if data_log:
            data = datetime.strptime(data_log, '%Y-%m-%d').strftime("%d/%m/%Y")
        else:
            data = datetime.now().strftime("%d/%m/%Y")
        
        # Atualiza o peso atual do usuário
        current_user.peso = valor
        
        # Cria log para o gráfico
        novo_log = PesoLog(valor=valor, data=data, user_id=current_user.id)
        db.session.add(novo_log)
        db.session.commit()
        flash('Peso atualizado com sucesso!', 'info')
    except (ValueError, KeyError):
        flash('Valor de peso inválido.', 'error')
    
    return redirect(url_for('home'))

@app.route('/refeicoes')
@login_required
def mostrar_refeicoes():
    refeicoes = Refeicao.query.filter_by(user_id=current_user.id).all()
    return render_template('refeicoes.html', refeicoes=refeicoes)

@app.route('/add_refeicao', methods=['POST'])
@login_required
def add_refeicao():
    try:
        descricao = request.form['descricao']
        calorias = int(request.form['calorias'])
        data_log = request.form.get('data_log')
        if data_log:
            data = datetime.strptime(data_log, '%Y-%m-%d').strftime("%d/%m/%Y %H:%M")
        else:
            data = datetime.now().strftime("%d/%m/%Y %H:%M")
            
        nova = Refeicao(descricao=descricao, calorias=calorias, data=data, user_id=current_user.id)
        db.session.add(nova)
        db.session.commit()
    except (ValueError, KeyError):
        flash('Dados da refeição inválidos.', 'error')
    return redirect(url_for('mostrar_refeicoes', data=request.form.get('data_log')))

@app.route('/delete_refeicao/<int:id>')
@login_required
def delete_refeicao(id):
    refeicao = Refeicao.query.get_or_404(id)
    if refeicao.user_id == current_user.id:
        db.session.delete(refeicao)
        db.session.commit()
        flash('Refeição excluída.', 'info')
    return redirect(url_for('mostrar_refeicoes'))

@app.route('/exercicios')
@login_required
def mostrar_exercicios():
    exercicios = Exercicio.query.filter_by(user_id=current_user.id).all()
    return render_template('exercicios.html', exercicios=exercicios)

@app.route('/add_exercicio', methods=['POST'])
@login_required
def add_exercicio():
    try:
        nome = request.form['nome']
        calorias = int(request.form['calorias'])
        data_log = request.form.get('data_log')
        if data_log:
            data = datetime.strptime(data_log, '%Y-%m-%d').strftime("%d/%m/%Y %H:%M")
        else:
            data = datetime.now().strftime("%d/%m/%Y %H:%M")
            
        novo = Exercicio(nome=nome, calorias=calorias, data=data, user_id=current_user.id)
        db.session.add(novo)
        db.session.commit()
    except (ValueError, KeyError):
        flash('Dados do exercício inválidos.', 'error')
    return redirect(url_for('mostrar_exercicios', data=request.form.get('data_log')))

@app.route('/delete_exercicio/<int:id>')
@login_required
def delete_exercicio(id):
    exercicio = Exercicio.query.get_or_404(id)
    if exercicio.user_id == current_user.id:
        db.session.delete(exercicio)
        db.session.commit()
        flash('Exercício excluído.', 'info')
    return redirect(url_for('mostrar_exercicios'))

@app.route('/add_agua', methods=['POST'])
@login_required
def add_agua():
    try:
        quantidade_ml = int(request.form['quantidade_ml'])
        data_log = request.form.get('data_log')
        if data_log:
            # Para água, usamos apenas a data sem hora para simplificar o agrupamento se necessário
            data = datetime.strptime(data_log, '%Y-%m-%d').strftime("%d/%m/%Y 00:00")
        else:
            data = datetime.now().strftime("%d/%m/%Y %H:%M")
            
        nova_agua = Agua(quantidade_ml=quantidade_ml, data=data, user_id=current_user.id)
        db.session.add(nova_agua)
        db.session.commit()
    except (ValueError, KeyError):
        flash('Erro ao registrar água.', 'error')
    return redirect(url_for('home', data=request.form.get('data_log')))

@app.route('/add_lembrete', methods=['POST'])
@login_required
def add_lembrete():
    texto = request.form['texto']
    if texto:
        novo = Lembrete(texto=texto, user_id=current_user.id)
        db.session.add(novo)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/toggle_lembrete/<int:id>')
@login_required
def toggle_lembrete(id):
    lembrete = Lembrete.query.get_or_404(id)
    if lembrete.user_id == current_user.id:
        lembrete.concluido = not lembrete.concluido
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete_lembrete/<int:id>')
@login_required
def delete_lembrete(id):
    lembrete = Lembrete.query.get_or_404(id)
    if lembrete.user_id == current_user.id:
        db.session.delete(lembrete)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

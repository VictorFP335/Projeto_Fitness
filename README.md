# Assita o video explicação do funcionamento do web service cloud
https://youtu.be/ISwruId5Hyk

[![Vídeo no YouTube](https://img.youtube.com/vi/ISwruId5Hyk/0.jpg)](https://youtu.be/ISwruId5Hyk)

#  CaloriFit — Sistema de Análise de Dados

Projeto desenvolvido para ajudar usuários a registrarem suas refeições diárias e acompanharem o total de calorias consumidas de forma prática e rápida.

---

##  **Equipe**

- **Enzo Braggion Cyrino** — 23008519 — enzo.bc@puccampinas.edu.br  
- **Veronica Marques Ribeiro** — 21943055 — veronica.mr@puccampinas.edu.br  
- **Victor Furumoto Puttomatti** — 23007606 — victor.fp5@puccampinas.edu.br  

---

##  **Descrição Geral**

Muitas pessoas desejam controlar a alimentação e acompanhar a ingestão diária de calorias, mas acabam desistindo por falta de ferramentas simples e intuitivas.

O **CaloriFit** surge como uma solução prática, permitindo ao usuário:

- Registrar refeições diárias  
- Visualizar somatório de calorias  
- Acompanhar sua evolução nutricional  

---

##  **Dataset**

- **Fonte dos dados:** API pública / FoodData Central (USDA)  
- **Volume esperado:** *não definido*  
- **Licenciamento:** MIT ou ausência de restrição  

---

##  **Arquitetura da Solução**

###  Diagrama de Arquitetura
## 🔧 Arquitetura — Fluxo da Aplicação

```
User / Frontend (HTML + CSS + JS)
│
└─> Navegador acessa o domínio do Render
    (ex.: https://calorifit.onrender.com)
│
├─> Frontend envia dados via formulários
│     ├─ Registro de calorias
│     ├─ Registro de exercícios
│     ├─ Dashboard diário
│     └─ Gráficos (AJAX → /grafico-data)
│
│
Backend — Flask App (Python)
│
├─ /               → página inicial com dashboard
├─ /calorias       → CRUD de refeições/calorias
├─ /exercicios     → CRUD de treinos
├─ /grafico-data   → retorna JSON para plotar no chart.js
│
├─ Controllers
│     ├─ calories_controller.py
│     ├─ exercises_controller.py
│     └─ dashboard_controller.py
│
└─ Models (camada de acesso ao banco)
      ├─ calories_model.py
      ├─ exercises_model.py
      └─ db.py (conexão SQLite)
```




###  Diagrama do Banco de Dados  
![Imagem do WhatsApp de 2025-11-27 à(s) 17 05 51_dce87a41](https://github.com/user-attachments/assets/e84a18e0-20cd-4776-8c5a-006eb113c9f6)

---

##  **Componentes Principais**

###  **Frontend**
- HTML  
- CSS  
- Bootstrap  

###  **Backend**
- Flask (Python + Jinja2)

###  **Banco de Dados**
- SQLite (local)  
- OU Azure SQL Database  

###  **Hospedagem**
- Azure App Service  

###  **Armazenamento**
- Azure Blob Storage (logs, imagens, backups)

---

##  **Justificativa da Arquitetura**

- **Azure App Service:** facilita deploy de aplicações Flask e oferece escalabilidade automática.  
- **Azure SQL Database:** garante segurança, integridade e persistência dos dados.  
- **Azure Blob Storage:** ideal para armazenar arquivos estáticos, logs e backups.  

---

##  **Segurança**

- Autenticação via **login + senha criptografada**  
- Comunicação protegida via **HTTPS**  
- Controle de acesso baseado em usuário

---

##  **Referências**

- https://flask.palletsprojects.com/  
- https://azure.microsoft.com/pt-br/products/app-service/  
- https://azure.microsoft.com/pt-br/products/azure-sql/  
- https://getbootstrap.com/  
- https://fdc.nal.usda.gov/  

---

##  **Infraestrutura Azure**

- **App Service Plan:** B1 (Free Tier)  
- **Banco de Dados:** Azure SQL  
- **Storage Account:** logs e armazenamento de imagens  
- **Provisionamento:** via Portal Azure (ou Bicep/Terraform, se aplicável)

---

##  **Pipeline CI/CD**

- Repositório GitHub conectado ao **Azure App Service**  
- Deploy automático a cada push na **branch principal**

---

##  **Observabilidade e Desempenho**

- Monitoramento de logs via **Azure Monitor**  
- Registro de requisições  
- Acompanhamento de erros e métricas de saúde do app  

---

##  **Resumo da Arquitetura**

- Backend conectado a banco de dados  
- SAAS utilizando APIs + datasets de registro de calorias  
- Frontend com design prototipado  
- Dashboards interativos para análise nutricional  

---

##  Estrutura do Template

- Equipe  
- Descrição Geral  
- Dataset  
- Arquitetura da Solução  
- Componentes principais  
- Justificativa técnica  
- Referências  
- Segurança  
- Infraestrutura Azure  
- Pipeline  
- Observabilidade  



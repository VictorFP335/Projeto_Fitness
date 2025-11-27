TEMPLATE - README para o Projeto
CaloriFit
Sistema de Análise de Dados
Equipe
Enzo Braggion Cyrino — 23008519 — enzo.bc@puccampinas.edu.br
Veronica Marques Ribeiro — 21943055—veronica.mr@puccampinas.edu.br
Victor Furumoto Puttomatti-23007606-victor.fp5@puccampinas.edu.br
Descrição Geral
Muitas pessoas desejam controlar a alimentação e acompanhar quantas calorias consomem diariamente, mas acabam desistindo por falta de ferramentas simples.
 O CaloriFit foi criado para resolver esse problema, permitindo que o usuário registre suas refeições diárias e acompanhe o total de calorias consumidas de forma prática e rápida.

Dataset
Fonte dos dados (URL, API, dataset público etc.)
Volume de dados esperado(none)
Licenciamento do dataset (MIT or None)
Arquitetura da Solução
diagrama de arquitetura 




Banco de Dados Diagrama:



Componentes principais:
Frontend: HTML, CSS, Bootstrap


Backend: Flask (Python + Jinja2)


Banco de Dados: SQLite local ou Azure SQL Database


Hospedagem: Azure App Service


Armazenamento de arquivos e logs: Azure Blob Storage



Justificativa:
Azure App Service: escolhido por facilitar o deploy de aplicações Flask com escalabilidade automática.


Azure SQL Database: garante persistência e segurança dos dados.


Azure Storage: usado para armazenar logs e backups de dados.


Referências
Documentação do Flask


Microsoft Azure App Service


Azure SQL Database


Bootstrap


USDA FoodData Central


Segurança:
Autenticação via login e senha criptografada.


Conexão segura via HTTPS.


 Infraestrutura Azure
App Service Plan: B1 (Free Tier)


Banco de Dados: Azure SQL


Storage Account: para logs e imagens


Recursos provisionados via Portal Azure (ou Bicep/Terraform, se aplicável)
Pipeline CI/CD
Repositório GitHub conectado ao Azure App Service


Deploy automático a cada push na branch principa
Observabilidade e Desempenho
Logs de requisições monitorados pelo Azure Monitor


Arquitetura:


BD com backend 

criação de um SAAS conectando Apis e datasets de registros de calorias dos alimentos que serão selecionados para nosso clientes

Front end: design prototipado do app, análises com dashboards dinâmicos interativos


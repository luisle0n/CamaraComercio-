# act02-flask-app

# Pasos a seguir para deployar una aplicación flask en reder app

1. Crear un repositorio de GitHub llamado **act02-flask-app**
2. Clonar el repositorio en su entorno local
3. Instalar flask en su máquina local
4. Dentro de la carpeta clonada crear la siguiente estructura
```
├── app.py
├── README.md
└── requirements.txt
```

5. Modificar el archivo app.py con el siguiente contenido
  ``` python
  from flask import Flask
  from datetime import datetime

  app = Flask(__name__)

  @app.route('/')
  def home():
      actual = datetime.now()
      fecha_formateada = actual.strftime("%d, %B, %Y, %M, %H, %S")
      return f'¡Hola, mundo! <b>{fecha_formateada}</b>'

  if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000)
  ```
6. Probar que la app funcione bien en su entorno local, usar
  ```
  python app.py
  ```
  Y verificar en el navegador

7. Subir los cambios a GitHub
8. En en repositorio de GitHub, agregar el siguiente action con el nombre **render-deploy.yml**
  ```
  name: Deploy to Render

  on:
    push:
      branches:
        - main

  jobs:
    deploy:
      runs-on: ubuntu-latest

      steps:
      - name: Checkout código
        uses: actions/checkout@v3

      - name: Llamar webhook de Render
        run: curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```
---

9. Crear un cuenta en la plataforma render: https://render.com/ ; usar el plan free
10. Crear un Web Service en RENDER
11. A través de GitHub, vincular con el proyecto previo creado.
12. Agregar la siguiente información al proyecto web service en render
```
  Runtime: Python
  Build Command: pip install -r requirements.txt
  Start Command: python app.py
  Free Plan
```
13. Activar/verificar el Webhook Deploy.
13.1 En la app de Render, dirigirse a Settings > Deploy > Manual Deploys > Enable Deploy Hook y Copia el Webhook URL
14. Agregar el Webhook a GitHub como una variable secreto
14.1 En GitHub, ir a al repositorio > Settings > Secrets and variables > Actions
14.2 Crear un nuevo secreto:
```
Name: RENDER_DEPLOY_HOOK
Value: pega la URL del webhook que copiaste de Render
```
15. Realizar un cambio en el repositorio de GitHub, en el archivo app.py, desde el local y sube los cambios.
16. Se puede revisar los logs del proyecto en RENDER
17. Verificar que la app esté ejecutándose con los cambios

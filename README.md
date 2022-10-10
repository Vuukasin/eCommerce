## Getting Started

1. Clone the project
```bash
  git clone https://github.com/Vuukasin/eCommerce.git

  cd eCommerce
  git checkout <branch-name>
  rm -rf .git
  git init .
  git add .
  git commit -m "My eCommerce project"
```

2. Create virtual environment and activate it.
```bash
  python3.10 -m venv venv
  source venv/bin/activate
```
Use .\venv\Scripts\activate if on windows

3. Install requirements 
```bash
  (venv) python -m pip install pip --upgrade
  (venv) python -m pip install -r requirements.txt
```

4. Migrate models to db
```bash
  python manage.py migrate
```

#### You can load items from fixtures or create your own on admin panel
```bash
  python manage.py loaddata items.json
```

5. Open VSCode
```bash
  code .
```

## Demo (screenshots)
Home page

<img src="home_screenshot.png">
Checkout page

<img src"checkout_screenshot.png">

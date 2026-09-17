# sport_itmo

### Телеграмм бот записывающий студентов итмо на секции

### Можно записаться @sport_itmo_bot или запустить собственного.

### Запуск

#### Установите postgresql и настройте его
sudo apt install postgresql

#### Установите playwright и браузер
sudo apt install playwright

playwright install chromium

#### Установите репозиторий
git clone https://github.com/Marsenie/sport_itmo.git

#### Установите пакеты
python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

#### Создайте файл .env на подобии env.txt и вставте в него всё необходимое
#### Запустите main_bd.py
python3 main_bd.py
#### Запустите main.py
nohup python3 main.py &

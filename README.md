# Moneynote
![Website](https://img.shields.io/website?url=http%3A%2F%2F34.101.175.204%3A44444%2F)
![](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![](https://img.shields.io/badge/Bootstrap-563D7C?style=flat&&logo=bootstrap&logoColor=white)
![](https://img.shields.io/badge/PostgreSQL-316192?style=flat&&logo=postgresql&logoColor=white)
![](https://img.shields.io/badge/SQLite-07405E?style=flat&logo=sqlite&logoColor=white)
![](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat&&logo=google-cloud&logoColor=white)
## Deskripsi
 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
## Anggota Kelompok
|Nama|NIM|
|--|--|
|[Andyana Lilmuttaqina Mafaza](https://github.com/andyanamafaza4)|G6401211002
|[Irfan Alamsyah](https://github.com/irfanalmsyah)|G6401211029|
|Andra Dihat Putra|G6401211053|

## Daftar Isi
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Instalasi](#instalasi)
- [Tech Stack](#tech-stack)

# Entity Relationship Diagram
![ERD](static/entityrelationaldiagram.png)

# Schematic Diagram
![Schematic Diagram](static/schematicdiagram.png)

# Instalasi
<details>
    <summary>Dengan Docker</summary>
    <p>

## Prasyarat
- [Docker](https://docs.docker.com/get-docker/)

### 1. Clone repository ini
```bash
git clone https://github.com/irfanalmsyah/projectBasisData.git
```
### 2. Masuk ke direktori repository
```bash
cd projectBasisData
```
### 3. Buat file `.env` dari file [`.env.example`](.env.example)
```bash
cp .env.example .env
```
### 4. Jalankan docker-compose
```bash
docker-compose up
```
> server akan berjalan di `http://localhost:44444`
</details>
<details>
    <summary>Tanpa Docker</summary>
    <p>

## Prasyarat
- Python 3.9 atau lebih tinggi
- PostgreSQL jika ingin menggunakan database PostgreSQL
### 1. Clone repository ini
```bash 
git clone https://github.com/irfanalmsyah/projectBasisData.git
```
### 2. Masuk ke direktori
```bash
cd projectBasisData
```
### 3. Install dependensi
```bash
pip3 install -r requirements.txt
```
atau
```bash
python3 -m pip install -r requirements.txt
```
### 4. Buat file .env sesuai dengan [`.env.example`](.env.example)
```bash
cp .env.example .env
```
### 5. Masuk ke direktori `backend`
```bash
cd backend
```
### 6. Migrasi database
```bash
python3 manage.py makemigrations && python3 manage.py migrate
```
## 7. Jalankan server
```bash
python3 manage.py runserver
```
> Server akan berjalan di `http://localhost:8000`</p>
</details>

# Tech Stack
- [Django](https://www.djangoproject.com/)
- [Bootstrap](https://getbootstrap.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLite](https://www.sqlite.org/index.html)





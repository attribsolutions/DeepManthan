FROM python:3.13.1-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc libmariadb-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/
COPY ./FoodERP/manage.py /app/

COPY ./FoodERP/FoodERP /app/FoodERP/
COPY ./FoodERP/FoodERPApp /app/FoodERPApp/
COPY ./FoodERP/FoodERPDBLog /app/FoodERPDBLog/
COPY ./FoodERP/SweetPOS /app/SweetPOS/
COPY ./FoodERP/media /app/media/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "FoodERP.wsgi:application"]








# FROM python:3.13.1-slim

# WORKDIR /app

# RUN apt-get update && \
#     apt-get install -y gcc libmariadb-dev pkg-config && \
#     rm -rf /var/lib/apt/lists/*

# COPY ./requirements.txt /app/
# COPY ./manage.py /app/


# COPY ./auth_app /app/auth_app/
# COPY ./backend /app/backend/

# RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE 8000

# # CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# # CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "backend.wsgi:application"]
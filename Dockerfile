FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

ENV SECRET_KEY="!tsyo30sxj#y1moxv40_z-%sridupa0paiow-e)emci9jlwjq*#"
ENV DEBUG="True"
ENV PORT=8000
ENV ALLOWED_HOST_1="127.0.0.1"
ENV ALLOWED_HOST_2="todoovers-habitica.grizwold.com"

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:$PORT"]
FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stitch.py .

CMD bash
#CMD [ "python", "/usr/src/app/stitch.py", "-v", "-o", "data/results/cb.avi" ]


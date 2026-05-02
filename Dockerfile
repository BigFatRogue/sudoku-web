FROM python:3.11-slim
RUN groupadd -r groupsudoku
RUN useradd -r -g groupsudoku usersudoku
RUN pip install --upgrade pip
ENV PYTHONUNBUFFERED=1
WORKDIR /sudoku
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . . 
EXPOSE 8000
USER usersudoku
CMD ["python", "run.py"]
 
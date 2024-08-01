FROM python:3.10
ENV APP /app
RUN mkdir $APP
WORKDIR $APP
EXPOSE 5000
 
RUN mkdir ./log

RUN pip install --upgrade pip
ADD requirements.txt .
RUN python -m pip install -r requirements.txt
 
# Add a new user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser
 
# Change the ownership of the working directory
RUN chown -R appuser:appuser /app
 
# Switch to the new user
USER appuser

#COPY . .
#CMD ["python", "/app/main.py"]

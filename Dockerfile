# Use Miniconda 3
FROM continuumio/miniconda3:latest

# Install Git
RUN apt-get install git
# Set the working directory
WORKDIR /biogame
# Assuming you're running docker-compose from the project directory after git clone
COPY . .
# Use conda-forge
RUN conda config --add channels conda-forge
RUN conda config --set channel_priority strict
# Downgrade Python
RUN conda install python=3.6.15 -y
# Create new environment
RUN pip install -r requirements.txt
# Copy the otree_tags to the new environment
RUN cp /biogame/Lottery/otree_tags/otree_tags.py /opt/conda/lib/python3.6/site-packages/otree/templatetags/
# Set the otree server to run on start
CMD ["otree", "runserver", "-v", "3", "0.0.0.0:8000"]
FROM python:3.9.10
# Set the work directory as oTree
WORKDIR /oTree
# Copy everything into it
COPY . .
# Install everything needed (only running one python project here, no venv needed)
RUN pip install -r requirements.txt
# BELOW SET ENVIRONMENT VARIABLES NEEDED IF YOU NEED TO, I DON'T NEED TO FOR THE BUILD BUT YOU MAY NEED TO.
# ENV OTREE_ADMIN_PASSWORD=<<password here>>
# ENV OTREE_SECRET=<<secret key here>>
# ENV OTREE_AUTH_LEVEL=DEMO
# ENV OTREE_PRODUCTION=1
# ENV DATABASE_URL=postgres://user:pass@host:5432/db
# Run the server
CMD ["otree", "prodserver"]
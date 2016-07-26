FROM mercury/cookie-monster:latest
MAINTAINER "C. Monster Esq." <cmonster@sanger.ac.uk>

# Install HGI Cookie Monster implementation
WORKDIR /cookie-monster
COPY requirements.txt the_monster.sh ./
COPY hgicookiemonster ./hgicookiemonster/

# pip can go die in a fire
RUN pip uninstall -y cookiemonster \
                     hgicommon \
                     baton
RUN curl $(sed -rn "s|^git\+https://github.com/(.+).git@(.+)#egg=.+$|https://raw.githubusercontent.com/\1/\2/requirements.txt|p" requirements.txt) \
  | xargs pip install
RUN pip install -U -r requirements.txt

EXPOSE 5000
ENTRYPOINT ["./the_monster.sh"]

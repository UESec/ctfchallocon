FROM ruby:3.3-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    redis-server \
    redis-tools \
    curl \
    ca-certificates \
    procps \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

ENV APP_HOME=/srv/orange-printer
ENV SECRET_HOME=/opt/orange-plant

WORKDIR ${APP_HOME}

COPY Gemfile ${APP_HOME}/Gemfile
RUN bundle install

COPY app/ ${APP_HOME}/
COPY flags/ ${SECRET_HOME}/
COPY start.sh /usr/local/bin/start-orange-printer

RUN chmod +x /usr/local/bin/start-orange-printer \
    && test -f ${SECRET_HOME}/orange_reactor_recipe.flag \
    && chmod 400 ${SECRET_HOME}/orange_reactor_recipe.flag \
    && chown -R root:root ${APP_HOME} ${SECRET_HOME}

EXPOSE 4567

CMD ["/usr/local/bin/start-orange-printer"]

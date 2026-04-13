###########
# BUILDER #
###########
#
# Base stage for both building production artifacts and running tests
#

#
# Pull official base image
#
FROM python:3.13-alpine AS builder

#
# Set the user
#
USER root

#
# Set work directory
#
WORKDIR /usr/src/app

#
# Set environment variables
#
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#
# Install psycopg dependencies we will need to build the wheels and run tests
#
RUN apk update \
    && apk add postgresql-dev gcc python3-dev

#
# Copy the application code to /usr/src/app and upgrade PIP
#
COPY . .
RUN pip install --upgrade pip
RUN pip install .

############
# BUILDER2 #
############
#
# Base stage for both building production artifacts and running tests
#
FROM builder AS builder2

#
# Create wheels for installation on the production image
#
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -e .

#
# Install nodejs/npm, then install our node packages
#
RUN apk add nodejs npm && npm install

#
# Build our webpack, which will drop build artifacts into the static subdirectory
#
RUN npm run build

##########
# TESTER #
##########
#
# Test runner, for running pylint and the unit tests for coverage.
#
FROM builder AS tester

#
# Set work directory
#
WORKDIR /usr/src/app

#
# Install development requirements
#
RUN pip install '.[dev]'

#
# Run pylint
#
RUN pylint --disable=fixme .

##############
# Production #
##############

#
# pull official base image
#
FROM python:3.13-alpine AS production

#
# Create the directory for the app user
#
RUN mkdir -p /var/www/job-application-tracker

#
# Create the app user
#
RUN addgroup -S app && adduser -S app -G app

#
# Create the appropriate directories
#
ENV HOME=/var/www/job-application-tracker
ENV APP_HOME=/var/www/job-application-tracker/web
RUN mkdir $APP_HOME

#
# Set work directory
#
WORKDIR $APP_HOME

#
# Install tzdata and set the timezone
#
RUN apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/America/New_York /etc/localtime \
    && echo "America/New_York" > /etc/timezone
ENV TZ=America/New_York

#
# Install SSL certificates authorities
#
RUN apk add --no-cache ca-certificates

#
# Install OS dependencies
#
RUN apk update && apk add libpq

#
# Copy over build artifacts from builder2 and install our wheels
#
COPY --from=builder2 /usr/src/app/wheels /wheels
COPY --from=builder2 /usr/src/app/static static
RUN pip install --upgrade pip \
    && pip install --no-cache /wheels/*

#
# Copy in the entrypoint script
#
COPY ./docker/py-wsgi/entrypoint.sh .
RUN chown root:root $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

#
# Copy in the project and clean up unwanted files
#
COPY . .
RUN rm -rf docker

#
# Chown all the files to the app user
#
RUN chown -R root:root $APP_HOME

#
# Run entrypoint.sh when we start up.
#
ENTRYPOINT [ "./entrypoint.sh" ]

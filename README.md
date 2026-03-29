# job-application-tracker
An application for tracking job applications

## Goal
While it certainly is something which could just use a spreadsheet for tracking the date,
company and job posting while looking for a job, I decided to use Django to write an application
for doing this as an exercise to keep the dust off my Django and Python skills as a side project.

This is a work in progress at the time of this writing.

## Base requirements

The base requirements for this application are those for Django 5.1, which according to the
release notes, is Python 3.10 or later, and npm. It is recommended to use Python 3.12, or perhaps 3.13,
though that has not been tested as of this writing.

## Setup

After cloning the repository, do the following steps:

1) Setup a virtual environment with the command `python3.12 -m venv .venv`.
2) Activate the virtual environment with the command `source .venv/bin/activate`.
3) Update pip with the command `pip install --upgrade pip`.
4) Load the requirements with the command `pip install -r requirements.txt`.
5) Load the static content using `npm install`.
5) Create a `.env` file following the `samples/env.sample` file as the model, and the credentials for a previously created database.
6) Create the application tables in the database using the command `python manage.py migrate`.

## Loading data

A sample spreadsheet can be uploaded to Google Documents then modified/loaded into the
application database using the command `python manage.py importsheet`. The API key and spreadsheet
id are a part of the `.env` file.

## Running the server

To run the server at the moment, issue the command `python manage.py runserver`.
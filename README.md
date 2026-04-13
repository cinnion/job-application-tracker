[![Build Status](https://www.ka8zrt.com:6963/buildStatus/icon?job=job-application-tracker&config=buildBadge)](https://www.ka8zrt.com/)
[![Testing Status](https://www.ka8zrt.com:6963/buildStatus/icon?job=job-application-tracker&config=testBadge)](https://www.ka8zrt.com/)
[![Coverage Status](https://www.ka8zrt.com:6963/buildStatus/icon?job=job-application-tracker&config=coverageBadge)](https://www.ka8zrt.com/)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

<!---toc start-->

* [job-application-tracker](#job-application-tracker)
* [Goal](#goal)
* [Base requirements](#base-requirements)
* [Setup](#setup)
* [Loading data](#loading-data)
* [Running the development server](#running-the-development-server)
* [Running as a development container](#running-as-a-development-container)
* [Deploying](#deploying)
* [A modest request](#a-modest-request)
* [Future features being considered](#future-features-being-considered)
* [Seeing it in action](#seeing-it-in-action)
* [Thanks](#thanks)

<!---toc end-->

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# job-application-tracker

A multi-user application for tracking job applications

# Goal

While it certainly is something which could, and did for a while, just use a spreadsheet for
tracking the date, company and job posting while looking for a job, I found that to be too cumbersome.
I was constantly doing a cut and paste of the company name or job title, and pasting the formatted string
into the spreadsheet. Clicking on the link to the job posting was not straight forward, and then trying to filter
entries by the company was ungainly once I had several hundred such entries. So I decided to use Django to write
an application for doing this as an exercise to keep the dust off my Django and Python skills as a side project.

It started off as a quick-and-dirty single user application which I originally had no intent for the public to see. But
then, it was suggested to me to make this a multi-user application, put it up for a demo site, and maybe even make it
available to others to use. And that functionality is all but done. However, it is still a work in progress, as I have
more ideas for features to be added in the future.

# Base requirements

The base requirements for this application were those for Django 5.1, which according to the
release notes, is Python 3.10 or later, and npm. However, it has since been upgraded to Django 6.0.3, and it is 
recommended to use Python 3.13.

# Setup

After cloning the repository, do the following steps:

1) Set up a virtual environment with the command `python3.13 -m venv .venv`.
2) Activate the virtual environment with the command `source .venv/bin/activate`.
3) Update pip with the command `pip install --upgrade pip`.
4) Load the base requirements with the command `pip install -e .`.
5) Load the development requirements with the command `pip install -e '.[dev]'`
6) Load the static content using `npm install`.
7) Build the build artifacts with `npm run build`.
8) Create a `.env` file following the `samples/env.sample` file as the model, and the credentials for a previously
   created database. Remember to generate the value for SECRET_KEY!
9) Create the application tables in the database using the command `python manage.py migrate`.
10) Create the superuser using `python manage.py createsuperuser`
11) Login to the Django Admin interface, create a user group, which has the `change_user_password`
    permission.
12) Through the Django Admin interface, create your user, which belongs to the user group you created.

NOTE: The next feature being added is going to be user registration, which will replace those steps.

# Loading data

Presently, the ability to import a spreadsheet has been removed pending refactoring as either
a file upload or via the Google API using a form for entering the API key and spreadsheet ID.
The previous implementation had no concept of this being a multi-user project.

# Running the development server

To run the server at the moment, use the command `runserver`, which is designed to run
the Django development server in one Xterm, and run WebPack in a second one.

# Running as a development container

There is a Docker Compose file, `docker-compose-dev.yml` for trying to run the application
in a dockerized environment. However, that has not been tested recently.

# Deploying

This project is set up to make use of a Jenkins job triggered by a GitHub webhook and using
the `Jenkinsfile` included with this project. It relies on my 
[Jenkins Build Tools Library](https://github.com/cinnion/jenkins-build-tools) to be installed
as a shared system library, along with the Jenkins plugins it requires. It is presently running
a CI/CD pipeline utilizing which makes use of a Jenkins secret file credential for running the
tests and coverage reports, which are then published to an internally available website, and
containers which are pushed to a private Docker registry and then run on a private Docker Swarm
with Docker Swarm secrets used to hold and supply the .env file to the application. You can
see this application in action [here](https://job-application-tracker.ka8zrt.com/). There is
a demo user with a credentials of 'demo' and the username with a space if you wish to see it
in action. 

# A modest request

Folks, I am putting this out there as Open Source, under the BSD 3-Clause license. While you are certainly free to 
fork this, modify it, etc. under the terms of the license, and even offer it to other users, I would ask that you 
instead work with me, and refrain from commercializing it yourself. Feel free to use it yourself, or better yet, when I
get user registration working, which will formally herald the V2.0 release of this software, register to use it on 
my site. For early adopters who are willing to work with me, I intend to make its use free. And this would continue 
even if I commercialize it myself. And if you have suggestions, please send them to me! Especially if I can get support
for this software, I would love to make it more useful to both myself and others... Which brings me to:

# Future features being considered

Among the ideas I have planned are the following.

- The first thing is to get user registration working. That is what differentiates this V1.something release from 
  the V2.0 release which is my near term goal. I am preparing to integrate [django-allauth]
  (https://docs.allauth.org/en/latest/), with its ability to do email verification during signup, and having 
  Multi-Factor Authentication. The first I view as being a mandatory feature, and 2FA is just as important. But that 
  work is going to take me at least a few days, given that I mostly had user support before I even came across 
  allauth. And sadly, while it uses Bootstrap for styling, its style does not match well with what I created. 
- One bit of low-hanging fruit I also intend to address is continue the work of moving tasks from the `Jenkinsfile` 
  into the shared library. After all, most of my projects today have me creating a `build_info.json` file with the 
  same information, and doing other steps.
- Providing for either a file upload or a form in which a Google API key and spreadsheet ID are entered, for 
  transitioning to using this software. When I first wrote this, I had nearly 400 job applications in a Google 
  Spreadsheet, an example of which you can find in the `samples` directory. And I had an admin command for `manage.py`
  which required the API key and spreadsheet ID in the `.env` file, which were then loaded by `settings.py`. But that
  makes no sense now, with this being a multi-user application. First, it would require contacting me to do the load
  of the data. Second, I would constantly be going through the hassles of putting those secrets, which I really do not
  want to know, into the .env file, and adding provisions for specifying the user ID. So I deleted that code, which I
  also had not place under test yet, to resurrect later.
- To go along with the file upload, I want to add the ability to download the job applications in spreadsheet form. This
  is something I have done with other projects which I wrote which used the [DataTables](https://datatables.net/) 
  library, and I know that sometimes, state unemployment agencies might request the data, so having this 
  functionality makes quite a bit of sense. And, if you are anything like me, it would give you some comfort knowing 
  that you had a backup of data which was hosted by somebody else on the net, be it Amazon or some individual.
- The ability to enter just the URL to the job post, and for sites like LinkedIn and a few others. Just click a 
  button to make an AJAX request which would return the minimal version of that URL, along with the company and job 
  title, to be populated into the form.
- Along with tracking job applications, I want to incorporate the ability to maintain the multiple versions of 
  resumes. I currently have two major versions of my résumé, a two-page version and a longer four-page version, 
  which is actually a superset of the two-page version. And my thought is to create templates, probably to a great 
  degree in code, to produce not only Word format documents which everyone wants, but to also use [LaTeX]
  (https://www.latex-project.org/), which is designed for actual typesetting of documents ranging from a few pages 
  upto multi-hundred monthly or quarterly technical journals, to produce PDF versions. And with the ability to 
  select jobs, and maybe even items for jobs for each version, I think that would be something useful to others as 
  well as to myself. And, it is something which has been floating around in my head as something to do, though I 
  originally thought to do it using [Laravel](https://laravel.com/). But given that is already exists, now it makes 
  more sense to add that functionallity here, rather than to a separate project.
- Maybe...maybe, reworking things to have a front-end written in React, and see about making it more responsive.

# Seeing it in action

As I mentioned earlier, if you wish to see the application in action, you can head on over to [my server]
(https://job-application-tracker.ka8zrt.com/). There is a demo user with a credentials of 'demo' and the username with
a space. Feel free to play with things. The only thing you won't be able to do is persist data for more than a few 
hours, and you won't be able to change or reset the demo user password. Other than that, it works just like it does 
for me. And if you would like to use it for yourself, as I know there are too many of us developers out there 
looking for jobs, before I have the registration page up, drop me a note, then provide me with feedback.

# Thanks

While not directly involved in either this or the Jenkins Build Library, I would like to thank my long-time friend
[Dave Weiner](https://github.com/dweinerATL), with whom I have and do work on a number of projects with. He is the one
who suggested I take this from a single user application I threw together quick and dirty to do
for me what Google Spreadsheets was not. And while like him, I could have probably done some of these things using
GitHub actions, Jenkins is something I learned to use in a previous job, and I quickly set up my own server to keep
those skills active.

Also, my thanks to the maintainer of [DocToc](https://github.com/ktechhub/doctoc). While I found their injection of
a link to their project a bit too glaring for inclusion in the head of my project, I still want to visibly thank them
for the tool with which I generate my table of contents, even if it does keep sticking that link in there, rather than
detecting a prior run, and just updating the table of contents.

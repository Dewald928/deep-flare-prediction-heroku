# deep-flare-prediction-heroku
Live flare prediction model on SHARP data

## Setup 
https://realpython.com/flask-by-example-part-1-project-setup/#installing-dependencies

1. Download and install conda
2. Create environment with `conda env create --file conda-env.txt `
3. If that doesn't work create a conda env with python 3.10.10 and run `pip instal -r requirements.txt`
4. Run flask in development mode: `FLASK_ENV=development flask run`

## Todo
* [x] Get current AR
* [x] basic html with latest picture
* [x] latest prediction per AR
* [ ] specify date & time -> get image and prediction
* [ ] make pretty -> css
* [ ] Incorporate MLP with history inputs (Lots of work)

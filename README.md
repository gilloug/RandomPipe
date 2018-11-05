# RandomPipe
A WEB page that play random youtube video each time you refresh it or click on the "reload" button.
Test the live demo at <https://randompipe.thamin.ovh>
___

This application uses ***docker-compose, python and flask***
___

To use it, just set the missing variables in the secrets.json file:
API_KEY -> you can get it at the url <https://randomyoutube.net/api>
APP_URL -> your application url, set it to http://127.0.0.1/ if you run the app in localhost
DEVELOPER_KEY -> your google project secret key, get it on the developers console
SECRET_KEY -> Your application secret key

Then you only have to launch
```
docker-compose up -d
```
To launch the app on the port 5000.
___

> I am open to issues and pull request, don't hesitate to participate and make this project bigger

# TinyURL

## Feature

- [x] Submit any URL and get a standardized, shortened URL back
- [x] Configure a shortened URL to redirect to different targets based on the device type (mobile, tablet, desktop) of the user navigating to the shortened URL
- [x] Navigating to a shortened URL should redirect to the appropriate target URL based on the device type
- [x] User can retrieve a list of all existing shortened URLs, including time since creation and target URLs (each with number of redirects)

## Installation

- Install Python
- Install Flask 
```bash
$ pip install Flask
```
- Get into the folder and run the Application
```bash
$ python tinyURL.py
```

## Usage

- to visit a shortenedURL, visit the URL like
```bash
localhost:5000/<shortenedCode>
```
**shortenedCode** is the code generated by the system<br>

eg: [localhost:5000/000001](localhost:5000/000001)

	> it will redirect you to the correct page based on the device you use.



- to submit an URL and get shortened URL, visit the URL like
```bash
localhost:5000/u/<userid>/<rawURL>
```
**userid** is the id of user who want to get the shortened URL<br>
**rawURL** is the url user want to shortened<br>

eg: localhost:5000/u/1/www.google.com




- to get a list of all existing shortened URLs of current user, visit the URL like
```bash
localhost:5000/u/<userid>
```
eg: [localhost:5000/u/1](localhost:5000/u/1)

    > `return data` is in json format, `result` is if this request get the answer user want, `data` is an array of all the URLs <br>
    > in one url, there is several parameters, list them as 'id', 'originalURL'(the URL redirected on the computer), 'mobileURL'(the URL redirected on the mobile phone), 'tabletURL'(the URL redirected on the tablet), 'originalTimes'(the times of redirects to the originalURL), 'mobileTimes'(the times of redirects to the mobileURL), 'tabletTimes'(the times of redirect to the tabletURL), 'shortenedURL'(the generated shortened URL), 'createDate'(The date this shortened URL created)




- to configure the URL should redirect to based on device, visit the URL like 
```bash
localhost:5000/u/<userid>/<shortenedCode>/config/<mode>/<newURL>
```
**userid** is the id of user who want to get the shortened URL
**shortenedCode** is the six Characters generated after slash in the shortenURL
**mode** is the mode user want to configure('mobile','tablet','desktop')
**newURL** is the new URL user want to change to in the mode of `mode`

eg: [localhost:5000/u/1/000001/config/mobile/m.google.com](localhost:5000/u/1/000001/config/mobile/m.google.com)

	> if succeed, `return data` include the modified url data, shown in the `data` part

# Analytics
Analytics is the Django application written by Box-in-a-Box ICT 2020 that functions as a tool to analyze data from the LRS and handles data sending to the [LLL (Lifelong Learning) platform](https://lll-platform.uu.nl/) through the [Boxconnect plugin](../../../boxconnect/README.md). The 3 most important components in the Analytics app are:

# URLS
The URLS functions as a mapping between [URL path expressions](urls.py) to [view functions](views.py). When the LLL platform requests analysis from Mofa it sends a request to Mofa, by calling [Boxconnect's Djangorequester's request function](../../../boxconnect/src/Djangorequester.php), which forwards the required analysis to Mofa's Analytics app. In order for Boxconnect to be able to connect with Mofa Boxconnect requires an authentication token. Creating and using an authentication token is explained in [authentication guide](authentication.md). In the Analytics app, based on the url/request that has been sent, a match is tried to be found between a list of urlpatterns and the url/request. When a match has been found, the corresponding view function of that match will be called. This view function will return a Response with the required analysis, which will be returned to the function that called the Djangorequester's request function.

# Views
The [view functions](views.py) are the functions that are doing the analysis over LRS data. It does this by sending a GET request to the LRS (queried on basis of the required data for the analysis). On the returned (JSON) content analysis will be done and the result of this will be parsed to a JSON format. This will then be usable for the function that requestedr the analysis.

# Test folder
The [test folder](test) contains the unit tests of the Analysis app.



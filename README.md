This repository is used to extract API data from Xandar Kardian API as well as Smarking's API for occupancy counts. 

The two data sources are then connected together in a table and uploaded via an .xlsx file. 

environment variables required:
-------------------------------
XK_API_KEY
SM_API_KEY
LocationID1
LocationID2
LocationID3
LocationID4
LocationID5
LocationID6

*locationID#'s correspond to smarking building ID's-- found via smarking URLs. 

As locations are added, the following needs to be adjusted:
-----------------------------------------------------------
Daily_Append.py & initial_data.py => adjust range in lines 72 & 76 in the respective .py files
Add additional LocationID's in the environment in numbered order

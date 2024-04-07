# BS/R Yield Curve Calculator

## Introduction
The purpose of this project is to plot a discrete-tenor par curve and a continuous monthly zero-rate curve with publicly available US Treasury curve data.

## Installation
The easiest way to run the project is with Make and Docker. Assuming both are installed, the application can be initiated and started by running:
`make fresh`
Once all services have been created and started, the application will be available at http://localhost:8000/admin/.

## Usage
Go to http://localhost:8000/admin/rates/treasurydata/add/ to add historical US Treasury data. Choose a date to load the data for and click the "Save and continue editing" button. This will pull the US Treasury data for the given date and display a chart of the calculated forward monthly zero rates. In order to download the output data to Excel or CSV, select the appropriate button at the bottom of the page.

== Note: Selecting a date that has already been downloaded or a date without any corresponding Treasury data will trigger an error. ==

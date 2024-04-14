echo 'preparing launch sequence  Please Wait ...'
source vnv/bin/activate

echo
echo 'Virtual environment activated ...'
echo 'Starting SitePlan services...'
nodemon siteplan/application.py

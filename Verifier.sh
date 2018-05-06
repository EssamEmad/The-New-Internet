FILE_NAME='TestingFile-1984.txt'
cd Clients
DIRS=$(find . -maxdepth 1 -mindepth 1 -type d)
# echo $DIRS
for DIR in $DIRS
do
cd $DIR
cmp $FILE_NAME ../../$FILE_NAME
cd ../
done
echo 'If there are no errors prior to this line, then its working'

echo 'Please note that if this script failed, it doesnt necessarily mean that the project'
echo 'is buggy. It could be that the shell script has failed, but the output was correct'
echo 'Enjoy =)\n\n'
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
echo 'If there are no errors prior to this line (After <enjoy =)>), then its working'

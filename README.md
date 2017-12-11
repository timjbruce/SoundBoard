# SoundBoard
Soundboard to play via Alexa

Pre-requisites:  Make sure the AWS CLI and Python 2.7 are installed locally on your computer.  Also, CLI must be setup for a 
region and user.

1. Run sbSetup.py <bucketname>, where bucket name is a bucket to be created for Alexa to retrieve your .mp3 files from.  A
dynamo table, soundboard, is also created
  
2. Create the sbStoreObject lambda function using the sbStoreObject.py function.  This needs to be triggered from objects
being stored in the s3 bucket.

3. Create the Alexa Skill for the soundboard (yes, I'm leaving most of the config open to whoever does this :))

  a. I've included the alexa.json file for you to create the intent and slots that I've used.

4. Create the sbSoundBoard.py lambda function and tie it to the Alexa skill from #3.

  a. Set environment variables for appid (your Alexa app id) and s3bucket (your bucket from #1)
  
5. Drop mp3 files in the s3 bucket using /show name/filename.mp3

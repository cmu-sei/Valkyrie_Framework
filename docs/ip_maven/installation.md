# How to use IP Maven

## Overview

The Whois and Mappings API endpoints can be accessed on the IP Maven UI or directly invoked using the URL.To see Mappings or Whois on the UI, navigate to /mappings or /whois on the browser. To invoke the API endpoints directly with the URL, navigate to /api/mappings or /api/whois.

## Prerequisite Steps

Follow instructions in the IP Maven Quick Start.

## Option 1: Docker container and github action

1. Download Docker desktop for your device.
2. Obtain permission to access IP Maven github repo. [Should be accomplished in Prerequisites]
3. Navigate to Actions tab.
4. Depending on your situation, either:

    <span style="color:gray">[IF CODE NOT MODIFIED]</span> Choose an existing 'Create Container' workflow that ran successfully (ex. this one)

    <span style="color:gray">[AFTER CODE MODIFIED AND CHANGES PUSHED TO GITHUB]</span> Run the 'Create Container' on the left menu. Select "Run workflow" and click green button. This may take a few minutes.

5. Once you are on the 'Create Container' page of a successful workflow run, scroll down to the 'Artifacts' section and download 'ipmaven'. You should end up with ```ipmaven.zip```  file.

6. Move the file to your desired location and open a terminal window in that directory.

7. Unzip the ```ipmaven.tar``` file in the same directory.

    ```shell
    unzip ipmaven.zip
    ```

8. In the same directory, run the following. This make take a few seconds.
    
    ```shell
    cat ipmaven.tar | docker load
    ```

9. Verify that ipmaven shows up.
    ```shell
    docker images
    ```

10. Replace the ```/path/to``` with your actual path to ipmaven and run the very long docker run command shown on the right hand side.

    ```-p out:in``` means the application is run on localhost:8888 but the actual container port is running on 8000
        * out (8888) can be changed to anything you want

    ```-v path/to/file:/app/ipmaven_www/file``` sets up a volume that mounts the local file at path ```path/to/file``` into the container directory ```/app/ipmaven_www/file```

    There are two instances of ```-v``` in the docker run command for the db.sqlite3 database that stores Whois data, and for the ```xxx.log``` file that stores Mapping data.
    
11. If you open docker desktop, you should be able to see the ipmaven container running.

12. As a sanity check, you may also click into the ipmaven container and navigate to the Files tabs, in which you should see that the db.sqlite3 and ```xxx.log``` files are in the correct location within app/
Go to ```http://localhost:8888/whois/``` and you should be able to view the data and use the UI to search and filter!

## Option 2: Local with downloaded github repo

Continue the instructions in the README of the repo. Namely, run:
```shell
python manage.py runserver 127.0.0.1:8000
```

Go to ```http://127.0.0.1:8000/whois/``` and you should be able to view the data and use the UI to search and filter!
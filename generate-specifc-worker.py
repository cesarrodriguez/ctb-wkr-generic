import os, shutil, sys, json, re, requests, subprocess

absolut_path_ctb_wkr_generic='../ctb-wkr-generic'

if not os.path.exists('/tmp'):
    os.mkdir('/tmp')
if not os.path.exists('/tmp/topic-mapping'):
    os.mkdir('/tmp/topic-mapping')

ctb_wkr_specific = input("Please enter CTB Worker Name: ")
print("You entered: " + ctb_wkr_specific)
if ctb_wkr_specific == '':
    print("[CTB WORKER NAME] is required! ")
    sys.exit()

governed_topic_name = input("Please enter Governed Topic Name suffix: ")
print("You entered: " + governed_topic_name)
if governed_topic_name == '':
    print("[TOPIC NAME] is required! ")
    sys.exit()

topic_mapping_json = input("Please enter json topic mapping -compact in 1 line - (Default look up in /tmp/field-mapping/"+ctb_wkr_specific+".json): ")
print("You entered: " + topic_mapping_json)
if topic_mapping_json == '':
    with open('/tmp/topic-mapping/' + ctb_wkr_specific + '.json', 'r') as jsonFile:
        topic_mapping_json = jsonFile.read()

if os.path.exists('../ctb-wkr-' + ctb_wkr_specific):
    shutil.rmtree('../ctb-wkr-' + ctb_wkr_specific)
else:
    print("The file does not exist")

os.mkdir('../ctb-wkr-' + ctb_wkr_specific)
for root, subdirectories, files in os.walk(absolut_path_ctb_wkr_generic):
    for subdirectory in subdirectories:
        print(os.path.join(root, subdirectory))
        absolut_folder_path = os.path.join(root, subdirectory)
        os.mkdir(absolut_folder_path.replace('ctb-wkr-generic', 'ctb-wkr-' + ctb_wkr_specific)
                 .replace('${workerName}', ctb_wkr_specific))
    for file in files:
        if '.py' in file or '.iml' in file:
            continue
        print(os.path.join(root, file))
        absolut_file_path = os.path.join(root, file)
        specific_absolut_file_path = absolut_file_path.replace('ctb-wkr-generic', 'ctb-wkr-' + ctb_wkr_specific) \
            .replace('${workerName}', ctb_wkr_specific)
        specificText = ''
        with open(absolut_file_path, 'r') as genericFile:
            genericText = genericFile.read()
            specificText = genericText.replace('${workerName}', ctb_wkr_specific) \
                .replace('${topicName}', governed_topic_name) \
                .replace('${workerNameTitle}', ctb_wkr_specific.replace('-', ' ').title().replace(' ', ''))\
                .replace('${workerNameTitleSpace}', governed_topic_name.replace('-', ' ').title())\
                .replace('${topicMapping}', topic_mapping_json)
            if '.json' in file:
                parsed = json.loads(specificText)
                specificText = json.dumps(parsed, indent=4, sort_keys=True)
        with open(specific_absolut_file_path, 'a') as specificFile:
            specificFile.write(specificText)

is_deploy = input("Would you like deploy this Worker?(yN): ")
print("You entered: " + is_deploy)
if is_deploy != 'y':
    print("[NO DEPLOY]")
    sys.exit()
print("[BEGINNING DEPLOY]")
item = input("Choose the server (Default is 1): \n 1. local \n 2. QA \n ")
if item == '1' or item == '':
    print("You entered: local")
elif item == '2':
    print("You entered: QA")
else:
    print("[NO CHOOSE] choose 1 to local or 2 to QA")
    sys.exit()
if item == "1" or item == '':

    print("[CREATING FILE] creating temp files and folders")
    os.mkdir('temp')
    os.mkdir('temp/ctb-wkr-' + ctb_wkr_specific)
    for root, subdirectories, files in os.walk('../ctb-wkr-' + ctb_wkr_specific):
        for subdirectory in subdirectories:
            absolut_folder_path = os.path.join(root, subdirectory)
            relative_folder_path = 'temp/ctb-wkr-' + ctb_wkr_specific + '/' + subdirectory
            os.mkdir(relative_folder_path)
        for file in files:
            absolut_file_path = os.path.join(root, file)
            temp_absolut_file_path = absolut_file_path.replace('ctb-wkr-' + ctb_wkr_specific, 'ctb-wkr-generic/temp/ctb-wkr-' + ctb_wkr_specific)
            specificText = ''
            with open(absolut_file_path, 'r') as specificFile:
                specificText = specificFile.read()
                if 'docker-compose' in file:
                    specificText = re.sub('SPRING_KAFKA_BOOTSTRAP_SERVERS:.*','SPRING_KAFKA_BOOTSTRAP_SERVERS: http://broker:29092' , specificText)
                    specificText = re.sub('SPRING_KAFKA_PROPERTIES_SCHEMA_REGISTRY_URL:.*','SPRING_KAFKA_PROPERTIES_SCHEMA_REGISTRY_URL: http://schema-registry:8081' , specificText)
                    specificText = re.sub('SPRING_KAFKA_CONSUMER_PROPERTIES_SCHEMA_REGISTRY_URL:.*','SPRING_KAFKA_CONSUMER_PROPERTIES_SCHEMA_REGISTRY_URL: http://schema-registry:8081' , specificText)
                    specificText = re.sub('SPRING_KAFKA_PRODUCER_PROPERTIES_SCHEMA_REGISTRY_URL:.*','SPRING_KAFKA_PRODUCER_PROPERTIES_SCHEMA_REGISTRY_URL: http://schema-registry:8081' , specificText)
                elif 'Dockerfile' in file:
                    specificText = re.sub('FROM.*','FROM localhost:5000/ctb-wkr-nottransac:latest' , specificText)
            with open(temp_absolut_file_path, 'a') as tempFile:
                tempFile.write(specificText)
subprocess.call("docker rm -f ctb-wkr-"+ctb_wkr_specific+"_ctb-wkr-"+ctb_wkr_specific+"_1", shell=True)
subprocess.call("docker rmi -f ctb-wkr-"+ctb_wkr_specific+"_ctb-wkr-"+ctb_wkr_specific, shell=True)
subprocess.call("docker-compose -f temp/ctb-wkr-"+ctb_wkr_specific+"/docker-compose.yaml up -d", shell=True)
#shutil.rmtree("temp")
##Description: 
The Partition Export/Import Template Engine helps in exporting and importing the complete Partition inventory on the same machine. The tool can also be used to create partition template from any given partition on the system and the template can be reused to create 'n' number of partitions on the same system

##Developers of the Tool: Preethi PY,Sowmya R, Anil k Paspuleti, Devagun


Note: The tool was implemented as part of Shrishti hackathon and this has also been the Idea from HVM-India team. This tool is not official and is also not tested in all scenarios. Hence the tool should be used at your own risk :)
********************************************************************************************************************************************************************************************************
The tool when used for importing partitions or creating partition from template, will have new WWPNs generated. So note that the SAN administrator has to reconfigure the WWPN to make the Luns visible on Partitions
********************************************************************************************************************************************************************************************************

How to Use the Tool:

=> Git clone the code from the repository to your local system "git clone https://github.com/preethipy/Partition_Export_Import_TemplateEngine.git"
=> The main script that has be run is export_import_template_engine/Console.py. The tool is quite interactive and hence very easy to use. 

Prerequisites:
=> The tool should can be run from any system which has access to HMC webservices API
=> Webservices API has to be enabled on HMC before starting to use the tool.

##1) Export Partition Inventory:

This feature helps you dump all the partition configuration on to your local system from where the tool is run. The sample execution output is shown below.

[preethi@localhost src]$ python Console.py 
****************************************************************************************************
                               Capture and replay partition creation                                
****************************************************************************************************
Enter HMC IP [9.152.151.49]              :9.152.151.49
Enter Username [pedebug]              :pedebug
Enter Password :
Establishing session.... /

|Fetching CPC List.... /
 done!
 done!
****************************************************************************************************
List of CPCs available
1    P000S67B

Select cpc by index from the given list [1]              :1
****************************************************************************************************
CPC P000S67B is selected
****************************************************************************************************
Choose one of the below options:

1.  create n partitions from existing templates?
2.  create a partition based on another partition?
3.  Export Partition Inventory?
4.  Import Partition Inventory? 

Select an option by index [4]              :3


Fetching Partition Inventory....... done!

****************************************************************************************************
Successfully Completed
****************************************************************************************************

##2) Import Partition Inventory:


This feature helps in importing the partition configuration of the same machine back to the system again

[preethi@localhost src]$ python Console.py 
****************************************************************************************************
                               Capture and replay partition creation                                
****************************************************************************************************
Enter HMC IP [9.152.151.49]              :9.152.151.49
Enter Username [pedebug]              :pedebug
Enter Password :
Establishing session.... /

|Fetching CPC List....   
 done!
 done!
****************************************************************************************************
List of CPCs available
1    P000S67B

Select cpc by index from the given list [1]              :1

****************************************************************************************************
CPC P000S67B is selected
****************************************************************************************************
Choose one of the below options:

1.  create n partitions from existing templates?
2.  create a partition based on another partition?
3.  Export Partition Inventory?
4.  Import Partition Inventory? 

Select an option by index [3]              :4
Creating Partition.... /
 done!
Creating VNics.... done!
Creating HBAs.... done!
Creating VirtualFunctions.... done!
Configuring Cryptos.... done!


Updating Partition Properties.... done!
Retrieve and Verify Partition Properties.... /
 done!
Partition: test Created Successfully
****************************************************************************************************
Successfully Completed
****************************************************************************************************

##3) Create a template from existing partition

This will help you create a template from any preferred partition and also lets you create n partitions based on the template.. Once template is created it is stored in the system locally.

[preethi@localhost src]$ python Console.py 
****************************************************************************************************
                               Capture and replay partition creation                                
****************************************************************************************************
Enter HMC IP [9.152.151.49]              :
Enter Username [pedebug]              :
Enter Password :
Establishing session.... /
-
-Fetching CPC List.... /
 done!
 done!
****************************************************************************************************
List of CPCs available
1    P000S67B

Select cpc by index from the given list [1]              :1

****************************************************************************************************
CPC P000S67B is selected
****************************************************************************************************
Choose one of the below options:

1.  create n partitions from existing templates?
2.  create a partition based on another partition?
3.  Export Partition Inventory?
4.  Import Partition Inventory? 

Select an option by index [4]              :2

1    test

Select partition by index [1]              :1

Enter the number of partitions to be created  [1]              :1
Fetching Partition Inventory....... /
 done!

****************************************************************************************************
Creating Partition 1
****************************************************************************************************
Creating Partition.... /
 done!
Creating VNics.... done!
Creating HBAs.... done!
Creating VirtualFunctions.... done!
Configuring Cryptos.... done!

Updating Partition Properties.... /
 done!

Retrieve and Verify Partition Properties.... done!
Partition: test_90DK Created Successfully
****************************************************************************************************
Successfully Completed
****************************************************************************************************

##4) Create n partitions from existing templates on your local system
If you have already created templates, you can create n number of partitions based on that template

[preethi@localhost src]$ python Console.py 
****************************************************************************************************
                               Capture and replay partition creation                                
****************************************************************************************************
Enter HMC IP [9.152.151.49]              :
Enter Username [pedebug]              :
Enter Password :
Establishing session.... /
\
-Fetching CPC List.... /
 done!
 done!
****************************************************************************************************
List of CPCs available
1    P000S67B

Select cpc by index from the given list [1]              :1

****************************************************************************************************
CPC P000S67B is selected
****************************************************************************************************
Choose one of the below options:

1.  create n partitions from existing templates?
2.  create a partition based on another partition?
3.  Export Partition Inventory?
4.  Import Partition Inventory? 

Select an option by index [2]              :1

Choose one of the below Templates:

1 .          test_template
2 .          HariTest1_template

Select a template available to create partition: []              :1

Enter the number of partitions to be created  []              :3

****************************************************************************************************
Creating Partition 1
****************************************************************************************************
Creating Partition.... /
 done!
Creating VNics.... done!
Creating HBAs.... done!
Creating VirtualFunctions.... done!
Configuring Cryptos.... done!

Updating Partition Properties.... /
 done!
Retrieve and Verify Partition Properties.... /
 done!
Partition: test_902R Created Successfully
****************************************************************************************************
Creating Partition 2
****************************************************************************************************
Creating Partition.... /
 done!
Creating VNics.... done!
Creating HBAs.... done!
Creating VirtualFunctions.... done!
Configuring Cryptos.... done!

Updating Partition Properties.... /
 done!
Retrieve and Verify Partition Properties.... /
 done!
Partition: test_A0WM Created Successfully
****************************************************************************************************
Creating Partition 3
****************************************************************************************************
Creating Partition.... /
 done!
Creating VNics.... done!
Creating HBAs.... done!
Creating VirtualFunctions.... done!
Configuring Cryptos.... done!

Updating Partition Properties.... /
 done!
Retrieve and Verify Partition Properties.... /
 done!
Partition: test_34L6 Created Successfully
****************************************************************************************************
Partition Created Successfully from template

****************************************************************************************************

****************************************************************************************************
Process Completed
****************************************************************************************************










# II Project

## Setting up the MES

It is possible to change the MES to interact with the PLC, the database and the UDP as long as they all share the same network. Under the file directory, the `config.json` should be changed with the IP of the machine running the respective service.

**Note**: All the arguments should be written surrounded by double quotation marks ("")

## Configuring the database

In order to install docker on windows please download the latest docker toolbox .exe release from [the official repo](https://github.com/docker/toolbox/releases).

**Notes**: You need to have Intel VT-x or AMD-V hardware virtualization enabled or the instalation will fail. If this happens, please enable it in your computers's BIOS and retry.

### Installing Docker

1.  Run the installer using the full instalation configuration and remember to tick the option to install VirtualBox.
2.  Run the Docker Quickstart Terminal shortcut and wait for the setup to finish.

### Setting up the database

1.	Open the Docker Quickstart Terminal or whichever shell you prefer (admin access may be needed)
2.	Navigate to the /II_project/db directory
3.	Run: `docker-compose up -d`
4.	After the containers are created you can check on them using: `docker ps`

### Remote access the database 

1.	Oracle VM VirtualBox should be installed by default after installing docker. Open the application
2.	Open the settigns and navigate to the Network tab
3.	Open Port Forwading under the Advanced options
4.	Create 2 new rules like the following  
		`Name: Rule 1, Host Port: 5050, Guest Port: 5050`  
		`Name: Rule 2, Host Port: 5432, Guest Port: 5432`


### Removing the database

To delete all containers and data run:

`docker-compose down --volumes` or `docker-compose down -v`

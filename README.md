# II Project

## Configuring the database

In order to install docker on windows please download the latest docker toolbox .exe release from [the official repo](https://github.com/docker/toolbox/releases).

**Notes**: You need to have Intel VT-x or AMD-V hardware virtualization enabled or the instalation will fail. If this happens, please enable it in your computers's BIOS and retry.

If you are running Windows 10 Pro, you can download [Docker Desktop](https://www.docker.com/products/docker-desktop) which uses native Hyper-V virtualization instead of VirtualBox. In order to be able to run the software in all versions of Windows 10 we chose to use the toolbox version. Choose whichever version you prefer at your own risk.

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
